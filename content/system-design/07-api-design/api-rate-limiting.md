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

You don't need a timer to add tokens. Store the token count and the time of the last top-up, and when a request arrives, add the tokens that would have dripped in since then:

```formula
b_new = min(C, b_old + r × Δt)
where
b_new: the number of tokens in the bucket after the top-up
b_old: the tokens stored at the last top-up
C: the capacity, the most tokens the bucket can hold
r: the refill rate, in tokens per second
Δt: delta t, the time since the last top-up, in seconds
min: the smaller of the two values, so the bucket never overflows its capacity
In words: add tokens for the time that has passed, but never more than the bucket holds.
```

If the bucket then holds less than one whole token, the request is rejected, and the client can be told how long until one token is ready:

```formula
W = (1 − b_new) / r
where
W: the wait until the bucket holds one whole token, in seconds; this is the natural Retry-After value
b_new: the tokens in the bucket now, less than 1
r: the refill rate, in tokens per second
In words: the missing fraction of a token divided by how fast tokens arrive. This only applies while b_new is below 1 (otherwise the request is allowed); Retry-After takes whole seconds, so send W rounded up.
```

The same logic as code (here `C`, `r`, `tokens` and `last_refill` are the capacity, refill rate, b and the stored time):

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

The refill one second after the burst, and the long-run rate:

```formula
b_new = min(10, 0 + 2 tokens/s × 1 s) = 2
R = 2 tokens/s × 60 s = 120 tokens
where
b_new: the tokens in the bucket one second after the burst emptied it
R: the most requests the client can make per minute once its burst is spent, one per token
tokens: the bucket's units; each request spends one
s: seconds
min: the smaller of the two values
In words: an empty bucket earns 2 tokens each second, so after the first burst the client is held to 2 requests per second, 120 per minute.
```

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

The worst-case extra delay is a full queue draining at the leak rate:

```formula
W_max = B / r
W_max = 100 / 50 = 2 s
where
W_max: the longest a request can wait in the queue, in seconds (s)
B: the queue size, in requests; here 100
r: the leak rate, in requests per second; here 50
s: seconds
In words: a request that joins the back of a full queue waits for every request ahead of it to leak out, so a 100-request queue at 50 per second adds up to 2 s.
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

It's extremely cheap: one counter per client per window. But it has a **boundary problem**. With a limit of 100/min, a client can send 100 at 12:00:59 and another 100 at 12:01:00. That's 200 requests in two seconds, double the intended rate:

```formula
A_max = 2 × L
A_max = 2 × 100 = 200
where
A_max: the most requests a fixed-window limiter can accept in a short span that straddles a window boundary
L: the limit per window, here 100 per minute
In words: the end of one window and the start of the next each allow the full limit, so a client timing its bursts can get twice the limit through in a couple of seconds.
```

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

It's exact, with no boundary problem. But it stores one entry per request in the window:

```formula
M = O(n)
where
M: the memory the log needs for one client
n: the number of requests that client made inside the window
O(...): Big O notation: how memory grows as n grows, ignoring constant factors
In words: memory grows in step with the client's traffic; at 10,000 requests per minute that's 10,000 stored timestamps for that one client.
```

As written, the read/count/conditional-add must run in a Lua script, or use `WATCH` with a read followed by `MULTI`/`EXEC` and retry on conflict. `MULTI` alone cannot branch on a queued `ZCARD` result; otherwise two servers can both read `count = 99` and both add.

This version only records *allowed* requests. If you record rejected ones too, a client that keeps hammering stays locked out until it actually backs off, a stricter policy some APIs choose deliberately.

### Sliding window counter

A clever approximation that keeps the cheapness of fixed windows and most of the accuracy of the log. Keep counts for the **current** and **previous** fixed windows, and weight the previous one by how much of it still overlaps the sliding window.

```formula
estimate = prev × (1 − t / W) + curr
where
estimate: the approximate number of requests in the last W seconds, compared with the limit
prev: the request count for the whole previous fixed window
curr: the request count so far in the current fixed window
t: the time elapsed since the current window started, in seconds
W: the window length, in seconds (60 for a per-minute limit)
In words: count all of this window's requests, plus the share of last window's requests that the sliding window still covers.
```

The weight 1 − t/W is the fraction of the previous window that still lies inside the sliding window: 1 at the start of the current window, falling to 0 at its end.

> [!example] Sliding window counter
> Limit 100/min. Previous minute: 80 requests. Current minute: 30 requests so far, and we're 15 s in, a quarter of the way through. The estimate is 90 (worked below). That's under 100, so allow. Ten more requests would push it to 100, after which further requests are rejected until the weighting decays.
>
> The weighting decays steadily. At 30 s in, the previous minute counts for half its 80, which is 40, so with 40 requests in the current minute the estimate is 80, leaving room for 20 more.

```formula
estimate = 80 × (1 − 15 s / 60 s) + 30
estimate = 80 × 0.75 + 30 = 90
estimate = 80 × (1 − 30 s / 60 s) + 40
estimate = 80 × 0.5 + 40 = 80
where
estimate: the approximate request count over the last 60 seconds
s: seconds
In words: 15 s into the minute, three quarters of the previous minute's 80 requests still count, giving 60 + 30 = 90; at 30 s only half count, giving 40 + 40 = 80.
```

The approximation assumes the previous window's requests were spread evenly. If all 80 arrived in its last second, the true count over the past 60 s is higher than the estimate, the error can be large under adversarial bursts.

Cloudflare described this approach in its 2017 implementation. In that workload’s analysis of 400 million requests from 270,000 distinct sources, only about 0.003% were wrongly allowed or limited.

### Summary

Memory is per client. O(1) means a fixed amount whatever the traffic; B is the leaky bucket's queue size, n the requests in one window and C the token bucket's capacity, as defined above.

| Algorithm | Memory | Bursts | Accuracy |
|---|---|---|---|
| Token bucket | O(1) | Up to C | Exact |
| Leaky bucket | O(B) | Smoothed | Exact |
| Fixed window | O(1) | 2× at edge | Poor |
| Sliding log | O(n) | Up to window quota | Exact rolling count |
| Sliding counter | O(1) | Workload-dependent | Approximate; error can be large for clustered arrivals |

## Distributed rate limiting

With 20 API servers behind a load balancer, a per-server in-memory limiter doesn't work: a client limited to 100/min could get 100 *per server*, or 2,000 in total:

```formula
L_eff = N × L
L_eff = 20 × 100 = 2,000
where
L_eff: the most requests per minute the client can actually get through the fleet
N: the number of servers, each with its own independent counter
L: the limit each server enforces, here 100 per minute
In words: independent limiters don't know about each other, so the real limit is multiplied by the number of servers the client can reach.
```

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

This teaching script assumes validated finite `C >= 1`, `r > 0` and a trusted timestamp in seconds. Arbitrary client timestamps must not reach it. Expiry must be no shorter than the time an empty bucket takes to refill completely; otherwise a slow-refilling bucket could expire and incorrectly reset to full:

```formula
T_full = C / r
TTL = max(1, ⌈T_full⌉)
TTL = max(1, ⌈10 / 0.1⌉) = 100 s
where
T_full: the time for an empty bucket to refill to capacity, in seconds (s)
C: the bucket capacity, in tokens
r: the refill rate, in tokens per second
TTL: time to live, how long Redis keeps the key before deleting it, in whole seconds
max: the larger of the two values, so the TTL is never below 1 s
⌈ ⌉: ceiling: round up to the next whole number
s: seconds
In words: keep the key at least as long as a full refill takes; a bucket of 10 refilling at 0.1 tokens per second needs 100 s.
```

Once that time has passed with no requests the bucket would be full anyway, so deleting the key and starting again full gives the same answer.

### Practical concerns

- **Latency.** Every request now makes a Redis round trip; measure median and tail latency under representative contention.
- **Fail open or closed?** If Redis is down, do you reject everything (closed) or allow everything (open)? A service may **fail open** with a local fallback limiter when availability is more important than temporary quota precision. Security-critical limits (login attempts) may fail closed.
- **Hot keys.** One huge tenant's counter lives on one Redis shard. Shard by client id across a Redis Cluster, and consider local pre-aggregation.
- **Clock skew.** The script above trusts `now` from whichever API server called it. If those clocks disagree, a server whose clock runs behind sees negative elapsed time. Use a trusted shared time source (for example Redis `TIME` in a compatible scripting/replication mode). The sample keeps the stored timestamp from moving backwards; merely clamping elapsed time while storing a lower timestamp can mint extra tokens when time catches up. Large forward jumps still require an explicit clock policy.
- **Approximate local limiting.** At very high scale, each server can enforce its share of the limit locally and sync periodically. It's less precise but needs no per-request network hop. The share is shown below.

```formula
L_local = L / N
L_local = 1,000 / 20 = 50
where
L_local: the limit each server enforces on its own, per minute
L: the client's overall limit, here 1,000 per minute
N: the number of servers sharing it, here 20
In words: split the limit evenly between the servers; this matches the global limit only when the client's traffic is spread evenly across all of them.
```

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
