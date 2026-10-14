---
id: arch-cache-hit-load-freshness
title: Relating cache hits to load and freshness
level: intermediate
minutes: 4
summary: Calculate cache read cost and database miss load while keeping each cache layer within its freshness policy.
sourceLesson: arch-scaling-reads
---

Read replicas add serving capacity but can lag. Caches keep frequently requested results close to readers; the calculation here measures their benefit using explicit hypothetical inputs.

## Caching layers

A cache stores the results of expensive reads in memory, typically Redis or Memcached, or at the edge in a CDN.

```
 client -> [CDN] -> [app + local cache]
                      |
                   [Redis]  hit
                      | miss
                   [ DB ]
```

Layers from the user inwards:

| Layer | Holds | Main considerations |
|---|---|---|
| Browser/CDN | Cacheable responses/assets | Cache policy and network distance |
| In-process | Hot keys | Per-instance freshness and memory |
| Distributed | Shared results | Network, load and consistency |
| Database buffer cache | Hot pages | Query work, locks and I/O |

> [!note] Evidence gap
> Fixed cache and database latency ranges are omitted because no measured environment supports them. The calculation below uses explicit hypothetical inputs.

The arithmetic is why caches matter. Every read checks the cache first. A **cache hit** is answered from the cache; a **miss** pays for the cache check *and* the database. The average read time and the share of reads that reach the database are:

```formula
T_avg = h × t_c + (1 − h) × (t_c + t_db)
F_db = 1 − h
where
T_avg: the average time per read, in milliseconds (ms)
h: the hit rate: the fraction of reads found in the cache, between 0 and 1 (95 % = 0.95)
t_c: the time for one cache lookup, in ms
t_db: the time for one database query, in ms
F_db: the fraction of all reads that still reach the database
ms: milliseconds, thousandths of a second
In words: the average is mostly the fast cache time, plus the misses' share of the slow path; only the misses load the database.
```

With a 95% hit rate, a 0.5 ms cache and a 20 ms database:

```formula
T_avg = (0.95 × 0.5 + 0.05 × 20.5) ms
T_avg = (0.475 + 1.025) ms = 1.5 ms
F_db = 1 − 0.95 = 0.05 = 5 %
where
T_avg: average time per read, in milliseconds (ms)
F_db: fraction of reads reaching the database
%: per cent; 0.05 = 5 %
ms: milliseconds
In words: reads average 1.5 ms instead of 20 ms, and only 1 read in 20 touches the database.
```

That's 20× less database load. Push the hit rate from 95% to 99% and F_db falls from 5% to 1%, so database load drops another 5×. The numbers are hypothetical inputs; real hit rates depend on how much of the data is hot, and the formula assumes every miss goes to the database (no second cache layer). Another module covers cache patterns, invalidation and stampedes in depth; architecturally, the key points are to cache close to the consumer, choose freshness, invalidation and eviction policies for each kind of data. A TTL is useful in many designs but does not alone bound source-data age; immutable content-addressed data can use different policies.

## Key takeaways
- Every miss pays for the cache lookup and the database under this single-cache model.
- Database load follows the miss fraction, so small hit-rate changes can have large effects on database traffic.
- Local cache copies can disagree; choose versioning, invalidation and source-age policies rather than assuming TTL alone guarantees freshness.

## Further reading
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
