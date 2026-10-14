---
id: api-leaky-fixed-window
title: Leaky buckets and fixed-window boundaries
level: advanced
minutes: 3
summary: Trade queueing delay for smooth output and recognise fixed-window boundary bursts.
sourceLesson: api-rate-limiting
---

## Leaky bucket

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

## Fixed window counter

Count requests per client in fixed clock windows: 12:00:00–12:00:59, 12:01:00–12:01:59, and so on.

Use a Redis Lua script so incrementing and assigning the first expiry happen atomically. The application supplies `KEYS[1]`, built from the trusted client identity and current calendar minute, and a validated positive integer limit in `ARGV[1]`. The expiry is a cleanup period from the first request; a different minute gets a different key.

```lua
-- KEYS[1] includes user and clock minute.
local limit = tonumber(ARGV[1])
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  -- Retain the counter through this minute.
  redis.call('EXPIRE', KEYS[1], 60)
end
-- 1 means allowed; 0 means rejected.
return count <= limit and 1 or 0
```

The counter includes rejected attempts too, but only the first request sets its expiry. Redis runs the script without interleaving other commands. Trusted key construction, validated inputs and Redis failure policy are still application responsibilities.

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

## Key takeaways
- A leaky queue smooths downstream traffic but adds waiting time and drops overflow.
- A fixed-window counter needs little state but can admit two windows’ quota across a boundary.
- NGINX nodelay changes queue behaviour by allowing immediate bursts while slots drain.

## Further reading
- [Cloudflare blog: How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Redis: Rate limiting](https://redis.io/glossary/rate-limiting/)
- [NGINX: Request limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
