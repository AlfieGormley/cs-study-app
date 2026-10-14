---
id: cache-redis-capacity-policies
title: Configure Redis capacity eviction
level: intermediate
minutes: 4
summary: Explain sampled eviction, memory overhead and the scope of allkeys and volatile policies.
sourceLesson: cache-eviction
---

Exact recency tracking consumes memory and updates metadata on reads. Redis approximates eviction and lets you select which keys may be victims when its accounted memory exceeds the limit.

## What real systems do

Exact LRU needs a linked list with two pointers per key and list updates on hits; shared concurrent implementations also need synchronisation. The pointers alone cost:

```formula
M_ptr = n × 2 × p
M_ptr = 100,000,000 × 2 × 8 B
M_ptr = 1,600,000,000 B = 1.6 GB
where
M_ptr: the memory used by the list pointers, in bytes (B)
n: the number of keys in the cache, here 100 million
2: two pointers per key, one to the previous entry and one to the next
p: the size of one pointer, in bytes; 8 B on a 64-bit machine
B: bytes; 1 GB = 1,000,000,000 B
GB: gigabytes
In words: each key carries 16 bytes of pointers, so 100 million keys spend 1.6 GB just on keeping the recency order.
```

At millions of keys and millions of reads per second, systems use **approximations**.

### Redis: sampled LRU and LFU

Redis does not keep a linked list. Each key stores a 24-bit field in its object header. In LRU mode it holds a coarse last-access clock. In LFU mode it holds an 8-bit frequency counter plus a 16-bit timestamp of the last decay.

When memory exceeds `maxmemory`, Redis:

1. Samples `maxmemory-samples` random keys (default **5**).
2. Adds the best candidates to a small **eviction pool** (16 entries) kept across rounds.
3. Evicts the best candidate in the pool.

Redis's documented comparison found five samples close to true LRU and ten closer, at extra CPU cost. Accuracy still depends on the access pattern; measure your workload.

Redis eviction policies, set via `maxmemory-policy`:

| Policy | Candidates | Rule |
|---|---|---|
| `noeviction` | none | Reject writes |
| `allkeys-lru` | all keys | Approx. LRU |
| `allkeys-lfu` | all keys | Approx. LFU |
| `volatile-lru` | keys with TTL | Approx. LRU |
| `volatile-lfu` | keys with TTL | Approx. LFU |
| `volatile-ttl` | keys with TTL | Soonest expiry |
| `*-random` | all / TTL | Random |

Redis 8.6 added `allkeys-lrm` and `volatile-lrm` (*least recently modified*), which only update the timestamp on writes, so keys that are read a lot but never updated can still be evicted.

> [!warning] The default is `noeviction`
> Out of the box, Redis does not evict. When its accounted memory is above the limit, memory-growing commands can fail with OOM while existing-key reads continue; maxmemory is not a strict RSS ceiling. For a pure cache you almost always want `allkeys-lru` or `allkeys-lfu`. The `volatile-*` policies evict nothing if no keys have a TTL.

## Choosing a policy

1. **Start with LRU** (`allkeys-lru`). It is a good default for most web workloads.
2. Switch to **LFU** if scans or one-off reads are polluting the cache, or if there is a stable set of popular keys.
3. Always set **TTLs** on data that can go stale, independent of the eviction policy.
4. **Measure**: watch `evicted_keys` and the hit ratio in Redis `INFO stats`. Many evictions with a falling hit ratio can indicate insufficient working-set capacity or a poor eviction policy.

## Key takeaways
- Redis samples candidates and retains an eviction pool instead of maintaining an exact recency list.
- The default noeviction policy rejects memory-growing commands; reads continue and maxmemory is not a strict RSS ceiling.
- Allkeys policies consider all keys; volatile policies need TTL-bearing keys. Separate persistent and disposable workloads when practical.

## Further reading
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis 8.6 features — Redis documentation](https://redis.io/docs/latest/develop/whats-new/8-6/)
