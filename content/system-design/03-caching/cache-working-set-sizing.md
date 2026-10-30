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

You rarely need to cache everything. Because access is skewed, the share of keys worth caching depends on the observed popularity distribution. The usual approach is:

1. Estimate the **working set**: the distinct keys touched in a typical window (an hour or a day). For a user-profile cache that is today's active users, not everyone who ever registered.
2. Multiply by the average size of one value plus the per-key overhead: the key itself, metadata and allocator waste. Measure that overhead with representative objects (Redis's `MEMORY USAGE` command reports a key's bytes); no fixed per-key overhead applies to every cache and data shape.
3. Add headroom for what the payload estimate leaves out: allocator fragmentation, client and replication buffers, snapshot copy-on-write and growth.
4. Measure the hit ratio at a few sizes. The curve of hit ratio against cache size flattens out; stop where extra memory stops buying meaningful hits.

```formula reference
M = K × (S_v + S_o)
where
M: the memory needed for the cached data, in bytes (B)
K: the number of distinct keys in the working set
S_v: the average size of one cached value, in bytes
S_o: the average overhead per key (the key itself, metadata and allocator waste), in bytes; measure it for your cache and data
B: bytes; 1 GB = 1,000,000,000 B
In words: payload memory is the number of active keys times what each one costs, value plus overhead. For example, 5 million active profiles of about 2 KB each, with about 100 bytes of measured overhead, need roughly 10.5 GB before any headroom.
```

The most common sizing mistakes are using all registered records instead of active ones (oversizing by the inactive majority), forgetting per-key overhead (which can rival the value for small items), and treating the payload total as the machine size.

## Key takeaways
- Estimate distinct active keys over a realistic window instead of caching every possible record.
- Include measured key, allocator and metadata overhead as well as the values themselves.
- Add measured fragmentation, buffers, replication and snapshot headroom, then compare hit ratios at different capacities.

## Further reading
- [MEMORY USAGE — Redis](https://redis.io/docs/latest/commands/memory-usage/)
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
