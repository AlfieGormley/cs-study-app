---
id: sepr-performance-algorithms
title: Reduce work before tuning instructions
level: intermediate
minutes: 4
summary: Evaluate algorithms, batching, caching and concurrency against measured bottlenecks.
sourceLesson: sepr-profiling
---

A profile tells you where the time goes, not what to do about it. The biggest wins usually come from doing less work, not from making each instruction faster. Whatever you change, keep the results, their order and any side effects the same.

## Step 3: the wins that matter
Candidate improvements to evaluate against measurements:

1. **Do less work.** Remove repeated computation, unneeded fields, duplicate calls.
2. **Better algorithms and data structures.** Reducing quadratic work to O(n log n), where n is the number of input items, improves scaling under comparable constant-time operations. Constants, memory use and workload size still determine the practical crossover.
3. **Batch I/O.** One query for 5,000 rows instead of 5,000 queries. Batch remote service requests, buffer writes.
4. **Cache** results that are expensive and reused, with a plan for invalidation.
5. **Concurrency** for I/O-bound work (asyncio, threads): overlap the waits.
6. **Move hot loops** to optimised code: NumPy vectorisation, a C extension, or a compiled language.
7. **Micro-optimisations** (local variable lookups, avoiding attribute access) last, and only in a proven hot loop.

A very common example of point 2:

```python
def common(a, b):
    # m is the number of items in b.
    # 'x in b' scans up to m values.
    return [x for x in a if x in b]

def common_fast(a, b):
    # Build once; values must be hashable.
    bs = set(b)
    # 'x in bs' is O(1) on average
    return [x for x in a if x in bs]
```

Both return the matching items of `a` in their original order, duplicates included; only the lookup changes. With 10,000 items in each list, `common` may compare each item of `a` against every item of `b`: up to 100 million comparisons. `common_fast` builds the set once and then does one hash lookup per item of `a`: about 20,000 operations. On one recent laptop (CPython 3.14), with 10,000 random integers in each list, the list version took about 0.4 seconds and the set version about 0.3 milliseconds. Your timings will differ, but the gap grows with the size of the lists.

The swap is only safe when its assumptions hold. The values must be hashable and must not change while in the set, and their equality and hashing must be ordinary. The set also costs extra memory in proportion to the length of `b`. Hash lookups are constant time on average, not in the worst case: many keys with colliding hashes can slow them down.

The same "do less work" idea applies to databases. A Django page that fetches 300 orders and then looks up each order's customer separately makes 301 queries: the **N+1 query** pattern. For a ForeignKey (each order has one customer), `Order.objects.select_related("customer")` fetches the customers with a join in the same query. For many-to-many relationships, `prefetch_related` instead adds one separate batched query. Fewer round trips usually help, but the joined query has its own cost, so measure it too.

## Key takeaways
- Reduce unnecessary computation and round trips before tuning tiny operations.
- A set can replace repeated list scans for stable hashable values, at an extra memory cost.
- Operation counts explain why one version scales better; only a measurement on your workload shows the actual speedup.

## Further reading
- [Python data model — hashing](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Django select_related and prefetch_related](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related)
