---
id: cache-working-set-sizing
title: Size a cache from its measured working set
level: basic
minutes: 3
summary: Estimate payload memory from active keys, value size and measured overhead, then reserve deployment headroom.
sourceLesson: cache-fundamentals
---

The number of registered records is usually less useful than the number of distinct keys read during the window you want to cover. Payload arithmetic is the starting point for sizing, not a complete machine recommendation.

## Sizing: how big should it be?

You rarely need to cache everything. Because access is skewed, the required fraction of cached keys depends on the observed popularity distribution. The usual approach is:

1. Estimate the **working set**: the distinct keys touched in a typical window (an hour or a day).
2. Multiply by average value size plus overhead (measure key, value, allocator and metadata overhead with representative objects; no fixed per-key overhead applies universally).
3. Measure the hit ratio at a few sizes. The curve of hit ratio against cache size flattens out; stop where extra memory stops buying meaningful hits.

Steps 1 and 2 as a formula:

```formula
M = K × (S_v + S_o)
where
M: the memory needed for the cached data, in bytes (B)
K: the number of distinct keys in the working set
S_v: the average size of one cached value, in bytes
S_o: the average overhead per key (the key itself, metadata and allocator waste), in bytes; measure it for your cache and data
B: bytes; 1 KB = 1,000 B, 1 MB = 1,000,000 B, 1 GB = 1,000,000,000 B
In words: memory is the number of keys you need to hold times what each one costs, including its overhead.
```

For example, 5 million active users with a 2 KB profile, under an illustrative 100-byte-overhead assumption:

```formula
M = K × (S_v + S_o)
M = 5,000,000 × (2,000 B + 100 B)
M = 10,500,000,000 B ≈ 10.5 GB
where
M: the memory needed, in bytes (B)
K: the number of keys, here 5 million active users
S_v: the value size, here 2 KB = 2,000 B
S_o: the assumed overhead per key, here 100 B
B: bytes
GB: gigabytes; 1 GB = 1,000,000,000 B
≈: approximately equal to
In words: 5 million profiles of about 2 KB each need about 10 GB for the values plus about 0.5 GB of overhead.
```

This is payload sizing, not a node recommendation; add measured fragmentation, buffers, replication and snapshot headroom.

## Key takeaways
- Estimate distinct active keys over a realistic window instead of caching every possible record.
- Include measured key, allocator and metadata overhead as well as the values themselves.
- Add measured fragmentation, buffers, replication and snapshot headroom, then compare hit ratios at different capacities.

## Further reading
- [MEMORY USAGE — Redis](https://redis.io/docs/latest/commands/memory-usage/)
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
