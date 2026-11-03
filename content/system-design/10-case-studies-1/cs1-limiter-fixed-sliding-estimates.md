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

```formula reference
E = P(1 − t / w) + C
where
E: estimated requests in the trailing window
P: requests counted in the previous aligned window
C: requests counted so far in the current aligned window
t: elapsed time in the current window, in seconds, from zero up to but excluding w
w: window duration in seconds
In words: count all current-window requests and estimate the still-overlapping part of the previous window; this assumes the previous requests were spread evenly.
```

Halfway through a window, the estimate keeps half the previous count and all of the current count. If earlier requests were concentrated near the boundary, that proportional estimate can be wrong.

- **Pro**: two integers per key, smooths boundary bursts.
- **Con**: approximate; it assumes requests in the previous window were evenly spread. Cloudflare reported around 0.003% incorrect decisions in its published workload. That historical empirical result is not a worst-case error bound; concentrated traffic can produce large errors.

## Key takeaways

- Fixed windows allow a double burst across an aligned boundary.
- Timestamp logs give exact counting semantics when implemented atomically.
- Two-window counters approximate a rolling interval and can err under concentrated traffic.

## Further reading

- [Cloudflare: measured sliding-counter approximation](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [Redis: atomic increment and rate-limit patterns](https://redis.io/docs/latest/commands/incr/)
