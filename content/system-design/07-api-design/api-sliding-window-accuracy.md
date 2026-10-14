---
id: api-sliding-window-accuracy
title: Sliding logs and approximate counters
level: advanced
minutes: 5
summary: Compare exact rolling counts with weighted-window estimates and their burst-sensitive error.
sourceLesson: api-rate-limiting
---

## Sliding window log

Store a timestamp for every request. On each new request, drop timestamps older than the window and count what's left.

In Redis, a sorted set does this neatly:

```pseudocode
# Remove allowed requests outside the
# window.
ZREMRANGEBYSCORE k 0 (now-60s)
ZCARD k            -> count
if count < limit:
  # A unique member prevents timestamp ties.
  ZADD k now req_id
EXPIRE k 60
```

It's exact, with no boundary problem. But it stores one entry per request in the window:

```formula
M = O(n)
where
M: the memory the log needs for one client
n: the number of accepted requests retained for that client inside the window
O(...): Big O notation: how memory grows as n grows, ignoring constant factors
In words: memory grows in step with the client's traffic; at 10,000 requests per minute that's 10,000 stored timestamps for that one client.
```

As written, the read/count/conditional-add must run in a Lua script, or use `WATCH` with a read followed by `MULTI`/`EXEC` and retry on conflict. `MULTI` alone cannot branch on a queued `ZCARD` result; otherwise two servers can both read `count = 99` and both add.

This version only records *allowed* requests. If you record rejected ones too, a client that keeps hammering stays locked out until it actually backs off, a stricter policy some APIs choose deliberately.

## Sliding window counter

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

The weight in the formula is the fraction of the previous window that still lies inside the sliding window: 1 at the start of the current window, falling to 0 at its end.

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

## Summary

Memory is per client. O(1) means a fixed amount whatever the traffic; B is the leaky bucket's queue size, n the requests in one window and C the token bucket's capacity, as defined above.

| Algorithm | Memory | Bursts | Accuracy |
|---|---|---|---|
| Token bucket | O(1) | Up to C | Exact |
| Leaky bucket | O(B) | Smoothed | Exact |
| Fixed window | O(1) | 2× at edge | Poor |
| Sliding log | O(n) | Up to window quota | Exact rolling count |
| Sliding counter | O(1) | Workload-dependent | Approximate; error can be large for clustered arrivals |

## Key takeaways
- A sliding log stores allowed request timestamps and needs an atomic count-and-add decision.
- A sliding counter weights the previous window by remaining overlap.
- Uniform weighting assumes evenly spread arrivals; clustered traffic can cause large errors.
- Historical Cloudflare measurements describe one workload, not an adversarial guarantee.

## Further reading
- [Cloudflare blog: How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Redis: Rate limiting](https://redis.io/glossary/rate-limiting/)
