---
id: arch-cache-hit-load-freshness
title: Relating cache hits to load and freshness
level: intermediate
minutes: 3
summary: Explain how cache hits reduce database work while keeping each layer within its freshness policy.
sourceLesson: arch-scaling-reads
---

Read replicas add serving capacity but can lag. Caches keep frequently requested results close to readers, exchanging freshness and maintenance work for faster reuse.

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

Every read in this model checks the cache first. A **cache hit** returns the cached result; a **miss** pays for both the cache lookup and the database query. More hits reduce database traffic and pull the average towards the cache lookup time. The optional model assumes fixed lookup costs and no extra cache layer:

```formula reference
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

Real hit rates depend on which data is popular and how long entries stay usable. Choose freshness, invalidation and eviction policies for each kind of data. A TTL bounds local residence time, but does not alone bound source-data age if an upstream copy was stale. Immutable content-addressed data can use different policies.

## Key takeaways
- Every miss pays for the cache lookup and the database under this single-cache model.
- Database load follows the miss fraction, so small hit-rate changes can have large effects on database traffic.
- Local cache copies can disagree; choose versioning, invalidation and source-age policies rather than assuming TTL alone guarantees freshness.

## Further reading
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
