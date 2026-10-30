---
id: cache-layered-misses-and-break-even
title: Judge stacked caches and when a cache pays off
level: basic
minutes: 3
summary: Follow misses through stacked caches and decide whether an extra lookup is worth its latency.
sourceLesson: cache-fundamentals
---

An upper cache changes the traffic a lower one sees. Judge each layer by what it saves the layer below, then compare the extra lookup cost with the backend time it avoids.

## Stacked caches

When caches sit in layers, each one sees only the misses of the layer above. A read reaches the database only if it misses *every* layer, so the share of reads that gets through is the first layer's miss ratio multiplied by the second layer's miss ratio, and so on.

For example, an in-process cache that answers half of all reads, in front of a Redis cache that answers 90% of what reaches it, lets through half of a tenth: 5% of reads reach the database, a combined hit ratio of 95%. This only works if each layer's hit ratio is measured on the traffic that actually reaches it.

A consequence surprises people: adding a fast upper layer usually makes the second layer's **own** hit ratio look worse. The in-process cache takes the hottest keys, so Redis is left with the harder, less repetitive reads. That is not Redis getting worse. Judge each layer by what it saves the layer below, and judge the stack by the share of reads that still reach the database.

> [!analogy] Real-world analogy: a sieve stack
> Gravel is shaken through a coarse sieve and then a fine one. The fine sieve now only sees what the coarse one let through, so it catches a smaller share of what reaches it than it would on its own, even though it works exactly as before. What matters is what ends up in the bin under the stack.
>
> **How it maps:** Each sieve is a cache layer, what passes through is the misses, and the second sieve's "catch rate" is the second cache's hit ratio measured on the traffic that reaches it. The bin under the stack is the database.
>
> **Where it stops:** Sieves sort by a fixed property (size). Caches decide by what they currently hold, which changes with eviction, expiry and the layer above.

## When does a cache lookup pay for itself?

A cache in front of a backend makes every read pay the lookup, and saves the backend time only on hits. If the backend is already fast or the hit ratio is low, the lookup can cost more than it saves. The hit ratio at which the two balance is the **break-even hit ratio**.

```formula reference
h_be = T_cache / T_backend
where
h_be: the break-even hit ratio, between 0 and 1; below it, the cache makes average latency worse than no cache
T_cache: the time for one cache lookup, in milliseconds (ms)
T_backend: the time for one backend read, in ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: a cache only improves average latency once its hit ratio beats the ratio of cache time to backend time. A 1 ms cache in front of a 20 ms database breaks even at about a 5% hit ratio; in front of a 2 ms backend it needs about 50%.
```

So a remote cache in front of a slow query almost always helps latency, while the same cache in front of a fast, well-cached database may not. Latency is not the only reason to cache, though: even a low hit ratio removes some backend load, and that can matter more.

## Key takeaways
- The share of reads reaching the database is the product of the miss ratios each layer sees on its own incoming traffic.
- A second-tier cache can show a weaker hit ratio because the cache in front already absorbed the hottest keys.
- A lookup only improves average latency when the hit ratio beats cache time divided by backend time; backend-load savings are a separate benefit.

## Further reading
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Cache (computing) — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
