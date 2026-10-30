---
id: cache-hit-ratios-and-latency
title: Relate hit ratio to latency and database load
level: basic
minutes: 4
summary: See why every read pays the cache lookup, and why the miss ratio decides how much traffic still reaches the database.
sourceLesson: cache-fundamentals
---

Measure both the time saved per request and the reads that still reach the database. A small latency improvement can hide a much larger change in backend load.

## Hit ratio and miss ratio

The **hit ratio** is the share of lookups the cache answers itself: 900 hits out of 1,000 lookups is a hit ratio of 0.9, or 90%. The **miss ratio** is everything else, here 10%. Count only lookups (reads), not writes, and count over a stated window such as a minute.

## Average read time

In the usual look-aside design every read checks the cache first, so **every** read pays the cache lookup, hit or miss. Only the misses then go on to pay for the backend as well. That gives the one relationship worth keeping in view:

```formula essential
T_avg = T_cache + (1 − h) × T_backend
where
T_avg: the average time to answer one read, in milliseconds (ms)
T_cache: the time for one cache lookup, hit or miss, in ms; measure it for your deployment
h: the hit ratio, between 0 and 1
(1 − h): the miss ratio, the fraction of reads that also go to the backend
T_backend: the time for the backend (for example the database) to answer one read, in ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: everyone pays for the cache lookup; only the misses also pay for the database. The higher the hit ratio, the closer the average gets to the cache's own speed.
```

Two predictions follow directly:

- **A slower cache slows every read.** If the Redis round trip grows (say the cache moves to another availability zone), hits *and* misses both get slower, because both pay the lookup.
- **Past a high hit ratio, latency barely moves.** With a 1 ms cache in front of a 20 ms database, going from a 90% to a 99% hit ratio takes the average from about 3 ms to about 1.2 ms. Going on to 99.9% only reaches about 1.02 ms, because the cache lookup now dominates.

This simple model assumes a miss is a cache lookup followed by a backend read, one after the other. It ignores the small extra cost of writing the loaded value back, and it describes the *average* only. Slow outliers (tail latency) need percentiles, not this formula.

## Database load follows the miss ratio

The database sees only the misses. Its read rate is the total read rate multiplied by the miss ratio, so it is the miss ratio, not the hit ratio, that sizes your database.

| Hit ratio | Miss ratio | DB reads per 10,000 |
|---|---|---|
| 0% (cache checked) | 100% | 10,000 |
| 90% | 10% | 1,000 |
| 99% | 1% | 100 |
| 99.9% | 0.1% | 10 |

Notice the asymmetry. Between 90% and 99% the average read time falls by less than 2 ms, but **database load falls tenfold**. From 99% to 99.9% the latency chart hardly moves, yet backend load falls by another 10×. When hit ratios are high, think in miss ratios.

This is also why losing a cache is so dangerous. If the database is sized for a 1% miss ratio and the cache disappears, it suddenly receives 100× its usual traffic. The later avalanche and warming units cover this failure mode.

## Key takeaways
- Every read pays the cache lookup; only misses also pay the backend in this sequential model.
- Backend load is proportional to the miss ratio, which can change tenfold while mean latency barely moves.
- Averages omit tail latency, refill costs and overload effects; a database sized for the misses needs a plan for cache loss.

## Further reading
- [Caching best practices — AWS](https://aws.amazon.com/caching/best-practices/)
- [Caching overview — AWS](https://aws.amazon.com/caching/)
