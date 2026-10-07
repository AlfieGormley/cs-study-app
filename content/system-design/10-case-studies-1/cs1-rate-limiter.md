---
id: cs1-rate-limiter
title: Design a distributed rate limiter
level: intermediate
minutes: 18
summary: Build a rate limiting service for a large API fleet, choosing between token bucket and sliding windows, keeping counters atomic in Redis, and deciding what happens when the limiter itself fails.
---

A rate limiter caps how many requests a client can make in a period. It protects services from abuse and runaway clients, enforces pricing tiers ("free plan: 100 requests per minute"), and stops one tenant from starving everyone else.

On one server it's an in-memory counter. The interview is about making it work across hundreds of API servers, at a million requests a second, adding no more than a millisecond, and staying correct when clients race each other.

## Step 1: Requirements

**Functional**

- Limit requests per **key** (API key, user ID, IP address, or a combination) according to **rules** such as "100 requests/minute per API key on `POST /charges`".
- Support several rules per request (per-second burst limit *and* per-day quota).
- When a limit is exceeded, reject with **HTTP 429 Too Many Requests** and tell the client when to retry.
- Rules can be changed without redeploying.

**Non-functional**

- **Low overhead**: the check sits on every request, so it must add under ~1–2 ms at p99.
- **Highly available**: if the limiter is down, the API should keep working.
- **Approximately accurate**: a small overshoot (a few percent) is fine; massively over-admitting is not.
- **Distributed**: limits are global across all API servers, not per server.

## Step 2: Estimates

Assume an API fleet handling **1 million requests/s** at peak, with **10 million active keys** a day.

```
Checks:   1M/s, 1 Redis call each
          (one Lua script per check)
Example: assume 50k checks/s per shard
         at the target tail latency
         -> 20 shards (plus replicas)
Memory:   assume 100 B per rule/key
          10M keys x 2 rules x 100 B
          -> ~2 GB
```

These are illustrative sizing inputs, not measured Redis capacity or memory bounds. Actual key strings, objects, allocator overhead, scripts, replication and network tails must be measured. A single atomic call reduces both race windows and network hops.

> [!note] Content gap: deployment benchmarks
> No reproducible deployment benchmark is supplied for the stated 1–2 ms target or per-shard throughput/footprint. Universal capacity and latency estimates are omitted; the calculation above uses explicit assumptions.

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

429 is defined in RFC 6585, and `Retry-After` is a standard HTTP header (RFC 9110). The `RateLimit-*` headers above come from early versions of an IETF draft; later versions fold them into structured `RateLimit` and `RateLimit-Policy` fields, and many APIs still use their own `X-RateLimit-*` variants (GitHub sends `x-ratelimit-limit`, `-remaining` and `-reset`, the last as a Unix timestamp). Whatever the names, good headers matter: well-behaved clients back off instead of hammering you.

> [!warning] Retry storms
> If every rejected client retries exactly at the `Retry-After` time, they all come back in the same instant. Client SDKs should add random jitter to retries, and the server can vary `Retry-After` slightly per client.

## Step 4: Data model

Two kinds of data:

**Rules** are small, read constantly, changed rarely. Store them in a database or config repo and push them to every limiter instance, which caches them in memory.

```
rule: domain=payments
      key=api_key, path=/charges
      limit=100, window=60s
      algorithm=token_bucket
```

**Counters** are tiny, extremely hot and short-lived. Keep them in Redis (or Memcached), keyed by rule and client:

```
rl:payments:/charges:{key_abc123}
  -> tokens=37
     last_refill=1727780000.123
```

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

## Deep dive 1: Algorithms

### Fixed window counter

Count requests in each calendar window (`12:00:00–12:00:59`); reject once the count passes the limit. One `INCR` plus an `EXPIRE`.

- **Pro**: trivial, one integer per key.
- **Con: boundary bursts.** With a 100/min limit, a client can send 100 at 12:00:59 and 100 more at 12:01:00, so 200 requests in two seconds.

### Sliding window log

Store a timestamp for every request (a Redis sorted set). On each request, drop entries older than the window and count what's left.

- **Pro**: exact.
- **Con: memory.** A limit of 10,000/hour stores up to 10,000 timestamps per key. At 10 million keys, that's prohibitive.

### Sliding window counter

Keep fixed-window counts for the current and previous window and weight the previous one by how much of it still overlaps:

```
estimate = prev x (1 - elapsed/window)
         + curr
```

If the previous minute had 80 requests, the current has 30, and we're 25% through it: `80 × 0.75 + 30 = 90`. Under a limit of 100, allow.

- **Pro**: two integers per key, smooths boundary bursts.
- **Con**: approximate; it assumes requests in the previous window were evenly spread. Cloudflare reported around 0.003% incorrect decisions in its published workload. That historical empirical result is not a worst-case error bound; concentrated traffic can produce large errors.

### Token bucket

Each key has a bucket of capacity `B` tokens, refilled at `r` tokens/second. Each request takes a token; an empty bucket means reject. Store just `tokens` and `last_refill`; refill lazily on each request:

```
tokens = min(B, tokens + (now - last) x r)
```

- **Pro**: allows controlled bursts (up to `B`) while enforcing a long-run average of `r`. Two numbers per key. This is what Stripe and AWS API Gateway use.
- **Con**: two parameters to tune; bursts are allowed by design, which might not suit a fragile downstream.

### Leaky bucket

Requests enter a FIFO queue drained at a fixed rate. Output is perfectly smooth, which suits traffic shaping in front of something fragile, but queued requests wait, and bursts are delayed rather than served. As a pure "allow or reject" meter, it behaves like a token bucket. GCRA (generic cell rate algorithm) is an elegant single-timestamp variant.

> [!tip] Default answer
> Token bucket for explicit burst-plus-average limits; sliding counters approximate rolling windows but do not provide exact rolling-window enforcement.

## Deep dive 2: Correctness under concurrency

Hundreds of gateway nodes check the same key at the same moment. A naive "read count, compare, write count + 1" is a race: two servers both read 99, both allow, both write 100, and the client got 101.

Fixes:

- **Atomic primitives.** For fixed windows, `INCR` is atomic and returns the new value: `INCR key`, then `EXPIRE key 60` on first creation, and compare the returned value with the limit. If the process dies between the two commands the key never expires, so do both in a Lua script or an appropriate transaction. Repeatedly extending a relative TTL changes expiration semantics unless the key includes the fixed window or the expiry is an absolute window boundary.
- **Lua scripts.** For token buckets, run the read-refill-decrement-write as a single Redis Lua script. Redis executes scripts atomically, so there are no races, and it's still one round trip.
- **Use the server's clock.** If every gateway passes its own `now`, clock skew between gateways distorts refills. Read time inside the script (`redis.call('TIME')`) so one clock is authoritative per key.

Redis Cluster maps keys to hash slots. The client-tag design co-locates that client's rules for one script; a global fleet counter or IP/account combination can require other slots, so arbitrary combined rules are not automatically atomic.

## Deep dive 3: Failure and degradation

The limiter must never be the reason your API is down.

- **Fail open.** If Redis times out (set an aggressive timeout like 5–10 ms), allow the request and emit a metric. Briefly over-admitting is better than rejecting all traffic.
- **Fail closed** only for limits that protect something critical, such as login attempts (brute-force protection) or expensive operations.
- **Local fallback.** Each gateway keeps an approximate in-memory bucket per key (global limit divided by the number of gateways). When Redis is unreachable, use that instead of nothing.

## Deep dive 4: Scaling the hot path

At a million checks a second, even one Redis round trip per request adds up. Options:

- **Local pre-check.** Gateways cache "this key is over limit until T" after a rejection, so a client hammering you is rejected locally without touching Redis.
- **Batching / lease tokens.** A gateway takes, say, 10 tokens at a time from Redis and spends them locally. Ten times fewer Redis calls, at the cost of slight inaccuracy (unused leased tokens). Only lease for keys whose limit is much larger than `gateways × lease size`: with 200 gateways leasing 10 each, a 100/min customer's whole allowance would be stranded on 10 gateways while requests on the other 190 are rejected.
- **Hot keys.** One huge customer can concentrate load on one Redis shard. Splitting the key into sub-buckets (`key#0..key#7`, each with 1/8 of the limit, picked at random) spreads it. The cost is accuracy: a request can be rejected by an empty sub-bucket while others still have tokens, so this only suits customers whose traffic is large enough to average out.

## Deep dive 5: Multiple regions

Should a global limit of 1,000/min be enforced across US and EU together? Synchronous cross-region checks add ~100 ms, which is unacceptable. Options:

- **Per-region limits**: give each region a share (e.g. proportional to its traffic). Simple, slightly unfair if traffic shifts.
- **Async sync**: each region enforces locally and gossips counts to the others every second or so. The global limit can be exceeded by roughly the traffic other regions admit during one sync interval. For a client sending near its limit that's a few percent; a client blasting all regions at once can overshoot by more, so pair this with a per-region burst cap.

Static regional shares can preserve a global quota if their allowances sum to the limit and redistribution cannot double-allocate. Asynchronous full-quota replicas instead need explicit overshoot and partition bounds.

## Bottlenecks and trade-offs

| Choice | Trade-off |
|---|---|
| Central Redis | Accurate, +1 hop |
| Local only | Fast, inaccurate |
| Fail open | Available, abusable |
| Fail closed | Safe, fragile |

Also mention that rate limiting is not load shedding. Stripe, for example, runs request-rate and concurrency limiters per user *and* fleet-wide load shedders that drop low-priority traffic when the whole system is under strain. Per-key limits don't protect you when a million well-behaved clients all arrive at once.

Rate is also not the same as work in progress. By Little's law, average in-flight requests = accepted arrival rate × mean duration in a stable system: a customer within a 100/min limit on a 20-second report endpoint holds about 33 requests in flight. A **concurrency limiter** (at most N in-flight requests per customer) bounds that directly.

## At 10x scale

At 10 million checks/s:

- A central Redis call per request may become expensive; shard count follows a representative script benchmark. Move to **two-tier limiting**: gateways enforce locally with leased tokens and sync with Redis every ~100 ms.
- Push coarse limits (per-IP DDoS protection) to the **edge/CDN** so abusive traffic never reaches your data centre.
- Use **per-region** limits, with periodic rebalancing of each region's share.
- Treat rule changes as a deployment: version them, roll them out gradually, and have a kill switch, because a wrong rule can reject all traffic instantly.

## Key takeaways

- Put the limiter in the gateway or a sidecar, backed by a sharded in-memory store; choose counter durability from the consequence of resets.
- Fixed windows allow 2x bursts at boundaries; sliding window logs are exact but memory-hungry; sliding window counters and token buckets are the practical choices.
- Avoid read-modify-write races with atomic `INCR` or a Lua script, and use one authoritative clock per key.
- Fail open by default; fail closed only for security-sensitive limits.
- Reduce hot-path cost with local rejection caches and leased tokens; accept small inaccuracy for large latency wins.
- Return 429 with `Retry-After` so clients back off, and add jitter so they don't all return at once.
- Choose the limiting key deliberately: authenticated IDs where possible, IP (and IPv6 prefixes) with care for shared addresses.
- In Redis Cluster, hash-tag the client key, not the rule, so one client's counters co-locate without creating a hot shard.

## Further reading

- [Stripe: scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Cloudflare: how we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Envoy: global rate limiting](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_features/global_rate_limiting)
- [Google Cloud: rate-limiting strategies and techniques](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [ByteByteGo: rate limiter for the real world](https://blog.bytebytego.com/p/rate-limiter-for-the-real-world)
- [Token bucket (Wikipedia)](https://en.wikipedia.org/wiki/Token_bucket)
- [RFC 6585: HTTP 429 Too Many Requests](https://www.rfc-editor.org/rfc/rfc6585)
