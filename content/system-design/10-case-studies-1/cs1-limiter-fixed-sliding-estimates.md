---
id: cs1-limiter-fixed-sliding-estimates
title: Compare fixed windows with rolling-count estimates
level: intermediate
minutes: 3
summary: Fixed windows allow a double burst across an aligned boundary.
sourceLesson: cs1-rate-limiter
---

A limiter rule might allow 100 requests per minute. The question is which minute: an aligned calendar interval or every possible rolling interval. This unit compares the counting algorithms before the next unit introduces a burst-and-average contract.

## Deep dive 1: Algorithms

### Fixed window counter

Count requests in each calendar window (`12:00:00–12:00:59`); reject once the count passes the limit. One `INCR` plus an `EXPIRE`.

- **Pro**: trivial, one integer per key.
- **Con: boundary bursts.** With a 100/min limit, a client can send 100 at 12:00:59 and 100 more at 12:01:00, so 200 requests in two seconds.

### Sliding request timestamp log

Store a timestamp for every request (a Redis sorted set). On each request, drop entries older than the window and count what's left.

- **Pro**: exact for the chosen rolling request-count interval when pruning, counting and recording accepted requests happen atomically.
- **Con: memory.** A limit of 10,000/hour stores up to 10,000 timestamps per key. At 10 million keys, that's prohibitive.

### Sliding window counter

Keep fixed-window counts for the current and previous window. A true rolling window ending now still overlaps the tail end of the previous window, so count the previous window in proportion to that overlap:

```formula
est = prev × (1 − t / w) + curr
est = 80 × (1 − 15 s / (60 s)) + 30
est = 80 × 0.75 + 30 = 90
where
est: the estimated number of requests in the last full window
prev: requests counted in the previous fixed window
curr: requests counted so far in the current window
t: time elapsed since the current window started, in seconds (s)
w: the window length, in seconds; here one minute = 60 s
t / w: the fraction of the current window that has passed, so 1 − t / w is the share of the previous window still inside the rolling window
s: seconds
In words: count the current window fully and the previous one only for the part that still falls inside the last minute; 25% into the minute, that is three quarters of the previous count.
```

So if the previous minute had 80 requests, the current has 30, and we're 25% through it, the estimate is 90. Under a limit of 100, allow.

- **Pro**: two integers per key, smooths boundary bursts.
- **Con**: approximate; it assumes requests in the previous window were evenly spread. Cloudflare reported around 0.003% incorrect decisions in its published workload. That historical empirical result is not a worst-case error bound; concentrated traffic can produce large errors.

## Key takeaways

- Fixed windows allow a double burst across an aligned boundary.
- Timestamp logs give exact counting semantics when implemented atomically.
- Two-window counters approximate a rolling interval and can err under concentrated traffic.

## Further reading

- [Cloudflare: measured sliding-counter approximation](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Redis: atomic increment and rate-limit patterns](https://redis.io/docs/latest/commands/incr/)
