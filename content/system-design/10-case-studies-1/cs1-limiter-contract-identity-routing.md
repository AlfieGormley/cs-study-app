---
id: cs1-limiter-contract-identity-routing
title: Choose identity, rule storage and shard routing
level: intermediate
minutes: 4
summary: Put checks before backend work and return useful retry guidance.
sourceLesson: cs1-rate-limiter
---

## Step 3: API

The limiter is usually an internal service called by the API gateway, or a library or sidecar inside it. Lyft's open-source Envoy rate limit service is a gRPC service with essentially this shape:

```
ShouldRateLimit(domain, descriptors[])
  -> {overall: OK | OVER_LIMIT,
      statuses: [{limit, remaining,
                  resetSeconds}]}
```

To the *external* client, a rejected request looks like:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 12
```

429 is defined in RFC 6585, and `Retry-After` is a standard HTTP header (RFC 9110). The `RateLimit-*` headers above are illustrative, non-standard field names from an earlier draft. The IETF HTTPAPI draft evolves structured quota fields; check the current draft rather than treating these names as a final standard. Many APIs still use their own `X-RateLimit-*` variants (GitHub sends `x-ratelimit-limit`, `-remaining` and `-reset`, the last as a Unix timestamp). Whatever the names, good headers matter: well-behaved clients back off instead of hammering you.

> [!warning] Retry storms
> If every rejected client retries exactly at the `Retry-After` time, they all come back in the same instant. Client SDKs should add random jitter to retries, and the server can vary `Retry-After` slightly per client.

## Step 4: Data model

Two kinds of data:

**Rules** are small, read constantly, changed rarely. Store them in a database or config repo and push them to every limiter instance, which caches them in memory.

Illustrative YAML configuration for this design, rather than an Envoy configuration format:

```yaml
# Identity and route choose the quota key.
domain: payments
key: api_key
path: /charges
# Capacity permits a burst of 100 requests.
capacity: 100
# Average allowance is 100 per 60 seconds.
refill_tokens: 100
refill_seconds: 60
algorithm: token_bucket
```

**Counters** are tiny, extremely hot and short-lived. Keep them in Redis (or Memcached), keyed by rule and client:

An illustrative Redis hash contains the balance and last refill time. These commands require a Redis connection; the timestamp is a fixture, not the current time.

```console
HSET rl:payments:/charges:{key_abc123} \
  tokens 37 last_refill 1727780000.123
HGETALL rl:payments:/charges:{key_abc123}
```

The hash contains 37 tokens and the supplied refill timestamp. Read, refill and decrement still need an atomic script; these two commands only demonstrate the stored representation.

The braces are a Redis Cluster **hash tag**: only the part inside `{}` is hashed to pick the shard. Tagging the *client* key puts all of one client's counters (burst limit, daily quota) on the same shard, so one Lua script can check several rules atomically, while different clients still spread across shards. Tagging the rule name instead (`{payments:/charges}`) would be a classic mistake: every client of that endpoint would land on one shard.

For this availability-first example, decide explicitly whether resetting counters is acceptable. A reset can grant a full new burst to every affected key, not merely a few percent overshoot. Security controls and billable quotas may require durable accounting or a different failure policy.

### Choosing the key

What you limit by matters as much as the algorithm:

- **API key or user ID** for authenticated traffic: precise and fair.
- **IP address** for anonymous traffic, with care. Thousands of mobile users can share one carrier-grade NAT address, and an IPv6 attacker can rotate through billions of addresses in a /64. Limit IPv6 by prefix (often /64) and set IPv4 limits loosely enough for shared addresses.
- **Combinations** for specific abuse: per (account, IP) limits on login can reduce some abuse, but distributed credential stuffing needs additional account/global signals and monitoring.

## Step 5: High-level design

```
 Client
   |
   v
 API gateway  <---- rules (cached,
   |   |              pushed on change)
   |   | check
   |   v
   | Limiter (lib/sidecar/svc)
   |   |
   |   v
   | Redis cluster
   | (counters, sharded by key)
   v
 Backend services
```

**Where to put it?**

- **In the client**: never trust it; clients can be modified.
- **In each service**: duplicated logic, inconsistent rules.
- **In the API gateway or a sidecar** (Envoy, Kong, AWS API Gateway): one place, before traffic reaches backends. This is the usual answer.
- **As a separate service** the gateway calls: centralises logic, costs an extra hop. Envoy's model is a sidecar that calls a central rate limit service backed by Redis.

## Key takeaways

- Put checks before backend work and return useful retry guidance.
- Hash-tag the client identity to co-locate its rules without one endpoint-wide hot shard.
- Consider NAT sharing, IPv6 rotation and retry jitter when choosing policy.

## Further reading

- [Envoy: global rate limiting](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_features/global_rate_limiting)
- [Redis: cluster hash tags](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [RFC 6585: HTTP 429](https://www.rfc-editor.org/rfc/rfc6585)
