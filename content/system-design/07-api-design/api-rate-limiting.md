---
id: api-rate-limiting
title: Rate limiting
level: advanced
minutes: 17
summary: Token bucket, leaky bucket, fixed and sliding windows, distributed rate limiting with Redis, and how to signal limits with 429 and Retry-After.
---

Rate limiting caps how many requests a client can make in a period. It's one of the most common system design interview questions, and one of the most important pieces of real API infrastructure.

## Why rate limit?

- **Protect the service.** One buggy client in a tight loop shouldn't take down everyone else.
- **Fairness.** Share capacity between tenants, so a noisy neighbour can't starve the rest.
- **Cost control.** Expensive endpoints (search, AI inference, SMS sending) cost real money per call.
- **Security.** Slow down credential stuffing, scraping and enumeration attacks.
- **Commercial tiers.** Free plan 60 requests/min, paid plan 5,000.

Stripe runs several limiters in layers: a request-rate limiter per user, a concurrent-requests limiter, and load shedders that drop low-priority traffic when the whole fleet is under stress.

## Signalling limits to clients

When a client is over its limit, return **429 Too Many Requests** (defined in RFC 6585), and tell it when to come back:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
RateLimit-Policy: "min";q=100;w=60
RateLimit: "min";r=0;t=12
Content-Type: application/problem+json

{"title": "Rate limit exceeded",
 "detail": "100 requests per minute"}
```

- `Retry-After` is a standard header: seconds to wait, or an HTTP date.
- `RateLimit-Policy` and `RateLimit` are being standardised by the IETF (still a draft in 2026). The policy says "quota `q` = 100 per window `w` = 60 s"; `RateLimit` says how much is left (`r`) and how many seconds until it resets (`t`). Earlier drafts used three separate `RateLimit-Limit`, `-Remaining` and `-Reset` headers, which some gateways still emit, and many APIs (GitHub, for example) use the older `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`. Note that GitHub's `X-RateLimit-Reset` is a Unix timestamp, not a number of seconds, so always read the docs.
- Send the remaining-quota headers on **successful** responses too, so well-behaved clients can slow down *before* hitting the wall.

Don't use `503` for per-client limits. `503` means "the service is unhealthy", which triggers different alerts and different client behaviour. (The reverse is fine: shedding load because the *whole fleet* is overloaded is a legitimate `503`.)

## The algorithms

### Token bucket

The most widely used algorithm. Each client has a bucket that holds up to **capacity** tokens. Tokens are added at a fixed **refill rate**. Each request takes one token; if the bucket is empty, the request is rejected.

```
  refill r tokens/s
        |
        v
   +---------+
   | o o o o |  capacity C
   | o o o   |
   +----+----+
        |
   1 token per request
   empty -> 429
```

Two parameters, two meanings:

- **Refill rate** = long-run average throughput.
- **Capacity** = largest burst allowed.

You don't need a timer to add tokens. Store `tokens` and `last_refill`, and top up lazily when a request arrives:

```
now = time()
elapsed = now - last_refill
tokens = min(C, tokens + elapsed * r)
last_refill = now
if tokens >= 1:
    tokens -= 1; allow
else:
    reject; retry_after =
      (1 - tokens) / r
```

> [!example] Token bucket maths
> Capacity 10, refill 2 tokens/s, bucket full. A client sends 15 requests instantly: the first 10 succeed, 5 get 429. One second later the bucket has 2 tokens, so 2 more can go through. Sustained, the client gets 2 requests/s, or 120 per minute.

Amazon API Gateway and AWS service APIs use token buckets (they call the parameters "rate" and "burst"). Stripe uses token buckets in Redis.

### Leaky bucket

Requests enter a **queue** of fixed size, and are processed (they "leak out") at a constant rate. If the queue is full, new requests are dropped.

```
 requests in (bursty)
     | | |||  |
     v v vvv  v
   +---------+
   | queue   |  size B
   +---------+
       |
       v  constant rate r
   to backend
```

The output is perfectly smooth, which is great for protecting a fragile downstream (say, a legacy system that can only handle 50 req/s). The cost is latency: bursty requests wait in the queue instead of being served immediately. NGINX's `limit_req` is a leaky bucket; its `burst` parameter is the queue size. Add `nodelay` and queued requests are served immediately instead, while still using up queue slots that drain at the set rate, so the behaviour becomes much closer to a token bucket.

| | Token bucket | Leaky bucket |
|---|---|---|
| Allows bursts | Yes, up to C | No (output smooth) |
| Excess requests | Rejected | Queued, then dropped |
| Adds latency | No | Yes |
| Typical use | Public APIs | Shaping to downstream |

### Fixed window counter

Count requests per client in fixed clock windows: 12:00:00–12:00:59, 12:01:00–12:01:59, and so on.

```
key = "rl:{user}:{minute}"
count = INCR key
if count == 1: EXPIRE key 60
if count > limit: reject
```

It's extremely cheap: one counter per client per window. But it has a **boundary problem**. With a limit of 100/min, a client can send 100 at 12:00:59 and another 100 at 12:01:00. That's 200 requests in two seconds, double the intended rate.

```
 limit 100/min
   window 1    |   window 2
 ..........100 | 100..........
          12:01:00
       200 in ~2 s
```

### Sliding window log

Store a timestamp for every request. On each new request, drop timestamps older than the window and count what's left.

In Redis, a sorted set does this neatly:

```
ZREMRANGEBYSCORE k 0 (now-60s)
ZCARD k            -> count
if count < limit:
  ZADD k now req_id
EXPIRE k 60
```

It's exact, with no boundary problem. But memory is O(requests) per client: at 10,000 requests/min, that's 10,000 entries per client. As written, the read/count/conditional-add must run in a Lua script, or use `WATCH` with a read followed by `MULTI`/`EXEC` and retry on conflict. `MULTI` alone cannot branch on a queued `ZCARD` result; otherwise two servers can both read `count = 99` and both add.

This version only records *allowed* requests. If you record rejected ones too, a client that keeps hammering stays locked out until it actually backs off, a stricter policy some APIs choose deliberately.

### Sliding window counter

A clever approximation that keeps the cheapness of fixed windows and most of the accuracy of the log. Keep counts for the **current** and **previous** fixed windows, and weight the previous one by how much of it still overlaps the sliding window.

```
estimate = prev * (1 - t/W) + curr
```

where `t` is time elapsed in the current window and `W` is the window length.

> [!example] Sliding window counter
> Limit 100/min. Previous minute: 80 requests. Current minute: 30 requests so far, and we're 15 s in (t/W = 0.25). Estimate = 80 × 0.75 + 30 = 60 + 30 = 90. That's under 100, so allow. Ten more requests would push it to 100, after which further requests are rejected until the weighting decays.
>
> The weighting decays steadily. At 30 s in, the previous minute counts for 80 × 0.5 = 40, so with 40 requests in the current minute the estimate is 80, leaving room for 20 more.

The approximation assumes the previous window's requests were spread evenly. If all 80 arrived in its last second, the true count over the past 60 s is higher than the estimate, the error can be large under adversarial bursts.

Cloudflare described this approach in its 2017 implementation. In that workload’s analysis of 400 million requests from 270,000 distinct sources, only about 0.003% were wrongly allowed or limited.

### Summary

| Algorithm | Memory | Bursts | Accuracy |
|---|---|---|---|
| Token bucket | O(1) | Up to C | Exact |
| Leaky bucket | O(B) | Smoothed | Exact |
| Fixed window | O(1) | 2× at edge | Poor |
| Sliding log | O(n) | Up to window quota | Exact rolling count |
| Sliding counter | O(1) | Workload-dependent | Approximate; error can be large for clustered arrivals |

## Distributed rate limiting

With 20 API servers behind a load balancer, a per-server in-memory limiter doesn't work: a client limited to 100/min could get 100 *per server*, or 2,000 in total.

```
 +----+ +----+ +----+
 |API1| |API2| |API3|
 +--+-+ +--+-+ +--+-+
    \     |     /
     +---------+
     |  Redis  |  shared
     +---------+  counters
```

A common design uses a **shared store** such as Redis for atomic operations and TTLs. Individual command atomicity does not make a multi-command read/modify/write sequence atomic, and failover durability is a separate concern.

### Race conditions

A naïve read-then-write has a race. Two servers both read `tokens = 1`, both allow, both write `tokens = 0`: two requests went through on one token.

Fixes:

- **Atomic commands.** `INCR` is atomic, but the conditional `EXPIRE` must also be protected from a crash between commands, for example by a Lua script. With a separate minute in the key, a missing expiry leaks old keys; with a reused key it can also lock out the client.
- **Lua scripts.** For token bucket, run the whole read-refill-decrement in a Lua script. Redis executes a script atomically, so no other command interleaves.

```
-- KEYS[1]=bucket
local C   = tonumber(ARGV[1])
local r   = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local b = redis.call('HMGET',
  KEYS[1], 'tokens', 'ts')
local tokens = tonumber(b[1]) or C
local ts = tonumber(b[2]) or now
-- Never move stored time backwards.
now = math.max(now, ts)
tokens = math.min(C,
  tokens + (now - ts) * r)
local ok = tokens >= 1
if ok then tokens = tokens - 1 end
redis.call('HSET', KEYS[1],
  'tokens', tokens, 'ts', now)
local ttl = math.max(1, math.ceil(C / r))
redis.call('EXPIRE', KEYS[1], ttl)
return ok and 1 or 0
```

This teaching script assumes validated finite `C >= 1`, `r > 0` and a trusted timestamp in seconds. Arbitrary client timestamps must not reach it. Expiry must be no shorter than the full refill time `C / r`; otherwise a slow-refilling bucket could expire and incorrectly reset to full.

### Practical concerns

- **Latency.** Every request now makes a Redis round trip; measure median and tail latency under representative contention.
- **Fail open or closed?** If Redis is down, do you reject everything (closed) or allow everything (open)? A service may **fail open** with a local fallback limiter when availability is more important than temporary quota precision. Security-critical limits (login attempts) may fail closed.
- **Hot keys.** One huge tenant's counter lives on one Redis shard. Shard by client id across a Redis Cluster, and consider local pre-aggregation.
- **Clock skew.** The script above trusts `now` from whichever API server called it. If those clocks disagree, a server whose clock runs behind sees negative elapsed time. Use a trusted shared time source (for example Redis `TIME` in a compatible scripting/replication mode). The sample keeps the stored timestamp from moving backwards; merely clamping elapsed time while storing a lower timestamp can mint extra tokens when time catches up. Large forward jumps still require an explicit clock policy.
- **Approximate local limiting.** At very high scale, each server can enforce `limit / N` locally and sync periodically. It's less precise but needs no per-request network hop.

> [!note] Measurement gap
> No benchmark establishes Redis latency, bytes per sorted-set member or a universal throughput cutoff here. These depend on deployment and data representation; measured capacity guidance is omitted.

### Where to enforce

Rate limiting usually lives at the **edge**: an API gateway, an Envoy sidecar, or a CDN (Cloudflare, AWS WAF). Enforcing it early means rejected requests cost almost nothing. Finer-grained, per-endpoint limits can live in the application.

Choose the **key** carefully: per API key or user for authenticated traffic; per IP for anonymous traffic (but remember many users can share one IP behind a corporate NAT or mobile carrier).

## Key takeaways
- Return **429** with **Retry-After**, and expose remaining quota on every response.
- **Token bucket**: refill rate = average throughput, capacity = burst. O(1) memory, lazily refilled. The default choice.
- **Leaky bucket** smooths output at the cost of queueing latency; good for protecting fragile downstreams.
- **Fixed window** is cheap but allows **2×** bursts at window boundaries. **Sliding log** is exact but O(n) memory. **Sliding window counter** is O(1) but can substantially undercount clustered traffic.
- In a fleet, use a **shared store** such as Redis with **atomic** operations or **Lua scripts** to avoid races.
- Decide whether to **fail open or closed**, watch for hot keys, and enforce at the edge.

## Further reading
- [Stripe blog: Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Cloudflare blog: How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Wikipedia: Token bucket](https://en.wikipedia.org/wiki/Token_bucket)
- [Redis: Rate limiting](https://redis.io/glossary/rate-limiting/)
- [MDN: 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [IETF draft: RateLimit header fields for HTTP](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [GitHub: Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
