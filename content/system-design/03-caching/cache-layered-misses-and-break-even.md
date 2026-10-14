---
id: cache-layered-misses-and-break-even
title: Calculate layered misses and latency break-even
level: basic
minutes: 4
summary: Multiply conditional miss ratios and decide whether a cache lookup repays its latency cost.
sourceLesson: cache-fundamentals
---

An upper cache changes the traffic a lower one sees. Use each layer’s hit ratio on its own incoming traffic, then compare the extra lookup cost with the backend time avoided.

### Stacked caches

When caches sit in layers, each one only sees the misses of the layer above. So the fraction of reads that gets all the way to the database is the product of the layers' miss ratios:

```formula
s_db = (1 − h_1) × (1 − h_2)
where
s_db: the share of all reads that reach the database, between 0 and 1
h_1: the hit ratio of the first (upper) layer, measured over the reads it sees
h_2: the hit ratio of the second layer, measured over only the reads the first layer missed
In words: the database sees what the first layer misses, and then only the part of that which the second layer also misses.
```

Suppose an in-process cache catches 50% of reads and Redis catches 90% of what is left:

```formula
s_db = (1 − h_1) × (1 − h_2)
s_db = (1 − 0.5) × (1 − 0.9)
s_db = 0.5 × 0.1 = 0.05
where
s_db: the share of all reads that reach the database
h_1: the in-process cache's hit ratio, here 0.5 (50%)
h_2: Redis's hit ratio on the reads that reach it, here 0.9 (90%)
In words: half the reads get past the in-process cache, and a tenth of those get past Redis, so 5% of reads reach the database.
```

Together they achieve a 95% hit ratio (1 − 0.05 = 0.95). The rule extends to any number of layers: multiply all their miss ratios. It assumes each layer's hit ratio is measured on the traffic that actually reaches it. Notice that Redis's *own* hit ratio can be lower than it would without the in-process layer, because the in-process cache has already taken the easiest, hottest keys. Judge each layer by what it saves the layer below, not by its ratio in isolation.

How low is "very low"? Without a cache every read costs the backend time. With one, every read pays the cache lookup and only misses also pay the backend, using the sequential model from the preceding latency unit. Setting the two equal gives the **break-even hit ratio**:

```formula
T_cache + (1 − h) × T_backend = T_backend
h_be = T_cache / T_backend
where
T_cache: the time for one cache lookup, in milliseconds (ms)
h: the hit ratio, between 0 and 1
T_backend: the time for one backend read, in ms
h_be: the break-even hit ratio; below it, the cache makes average latency worse than having no cache
ms: milliseconds; 1 ms = 0.001 seconds
In words: the cache pays for itself on latency once its hit ratio is bigger than the ratio of cache time to backend time.
```

For a 1 ms cache in front of a 20 ms database, the break-even hit ratio is 1 / 20 = 0.05, so 5%. Most real caches are far above this, but the same 1 ms cache in front of a fast backend (say 2 ms) needs a 50% hit ratio just to break even on latency. Latency is not the only reason to cache, though: even a low hit ratio still removes some backend load.

## Key takeaways
- Multiply the miss ratios measured on each layer’s incoming reads to find the share reaching the database.
- A lower cache can have a less impressive hit ratio because the upper cache already absorbed the hottest keys.
- Latency breaks even when the hit ratio equals cache time divided by backend time; backend-load savings are a separate benefit.

## Further reading
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
