---
id: cache-hit-ratios-and-latency
title: Calculate cache latency and database load
level: basic
minutes: 5
summary: Use hit and miss ratios to calculate mean read time and the backend traffic a cache absorbs.
sourceLesson: cache-fundamentals
---

Measure both the time saved per request and the reads that still reach the database. A small latency improvement can hide a much larger change in backend load.

## Hit ratio maths

To judge whether a cache is working, you count how many lookups it answers. The **hit ratio** is the fraction of lookups served from the cache, and the **miss ratio** is the fraction that fall through to the backend:

```formula
h = hits / (hits + misses)
m = 1 − h
where
h: the hit ratio, a number between 0 (nothing served from cache) and 1 (everything served); often written as a percentage, so 0.9 = 90%
hits: the number of lookups that found the key in the cache, counted over some window such as a minute
misses: the number of lookups that did not find the key and had to go to the backend, counted over the same window
m: the miss ratio, the fraction of lookups that reach the backend; also between 0 and 1
In words: the hit ratio is the share of lookups the cache answered itself, and the miss ratio is everything else.
```

For example, 900 hits and 100 misses in a minute give a hit ratio of 900 / 1,000 = 0.9 (90%) and a miss ratio of 0.1 (10%). Count only lookups (reads), not writes.

The **average access time** follows from this. Every request first looks in the cache, so every request pays the cache lookup. Only the misses then go on to pay for the backend as well. Weighting the backend time by the fraction of requests that pay it gives:

```formula
T_avg = T_cache + (1 − h) × T_backend
where
T_avg: the average time to answer one read, in milliseconds (ms)
T_cache: the time for one cache lookup, hit or miss, in ms; use a measured value for your deployment; the worked example assumes a 1 ms Redis round trip
h: the hit ratio, between 0 and 1
(1 − h): the miss ratio, the fraction of reads that also go to the backend
T_backend: the time for the backend (for example the database) to answer one read, in ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: everyone pays for the cache lookup; only the misses also pay for the database. The higher the hit ratio, the closer the average gets to the cache's own speed.
```

This simple model assumes a miss is a cache lookup followed by a backend read, one after the other. It ignores the small extra cost of writing the loaded value back into the cache, and it describes the *average* only. Slow outliers (tail latency) need percentiles, not this formula.

### A worked example

Redis takes 1 ms; the database takes 20 ms. At a 90% hit ratio:

```formula
T_avg = T_cache + (1 − h) × T_backend
T_avg = 1 ms + (1 − 0.9) × 20 ms
T_avg = 1 ms + 2 ms = 3 ms
where
T_avg: the average read time, in milliseconds (ms)
T_cache: the Redis lookup time, here 1 ms
h: the hit ratio, here 0.9 (90%)
T_backend: the database read time, here 20 ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: at a 90% hit ratio, the average read costs the 1 ms lookup plus a tenth of the 20 ms database time, 3 ms in total.
```

The database sees only the misses. Its read rate is the total read rate times the miss ratio:

```formula
R_db = (1 − h) × R
R_db = (1 − 0.9) × 10,000 = 1,000
where
R_db: the number of reads that reach the database
h: the hit ratio, here 0.9 (90%)
R: the total number of reads, here 10,000
In words: with a 90% hit ratio, only one read in ten reaches the database, so 10,000 reads become 1,000 database reads.
```

The table repeats both calculations for other hit ratios.

| Hit ratio | Average latency | DB reads per 10k |
|---|---|---|
| No cache lookup | 20 ms | 10,000 |
| 0% (cache checked) | 21 ms | 10,000 |
| 80% | 1 + 0.2×20 = 5 ms | 2,000 |
| 90% | 1 + 0.1×20 = 3 ms | 1,000 |
| 99% | 1 + 0.01×20 = 1.2 ms | 100 |

Notice what happens between 90% and 99%. Latency only falls from 3 ms to 1.2 ms, but **database load falls tenfold**, from 1,000 to 100 reads. The useful number is often the miss ratio (1 − h), because that is what your backend actually sees. Going from 99% to 99.9% barely registers on a latency chart (1.2 ms to 1.02 ms), but it cuts backend load by another 10×.

This is also why losing a cache is so dangerous. If the database is sized for a 1% miss rate and the cache disappears, it suddenly receives 100× its usual traffic. The later avalanche and warming units cover this failure mode.

## Key takeaways
- Every read pays the cache lookup; only misses also pay the backend in this sequential model.
- Calculate backend load from the miss ratio, which can change tenfold while mean latency barely moves.
- Averages omit tail latency, refill costs and overload effects; cache loss requires capacity and failure planning.

## Further reading
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
- [Caching overview — AWS](https://aws.amazon.com/caching/)
