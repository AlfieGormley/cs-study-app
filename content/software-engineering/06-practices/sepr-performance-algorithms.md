---
id: sepr-performance-algorithms
title: Reduce work before tuning instructions
level: intermediate
minutes: 3
summary: Evaluate algorithms, batching, caching and concurrency against measured bottlenecks.
sourceLesson: sepr-profiling
---

The profile identifies a candidate, not the correct intervention. Preserve ordering, values and side effects while testing whether less work meets the target.

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

With 10,000 items in each list, the two versions differ enormously in the work they do:

```formula
C_list = n_a × n_b
C_list = 10,000 × 10,000 = 100,000,000
C_set ≈ n_b + n_a
C_set ≈ 10,000 + 10,000 = 20,000
where
C_list: the worst-case number of equality comparisons `common` makes, scanning list b once for every item of a
C_set: a coarse count of set-insertion attempts plus membership lookups, assuming average constant-time hashing and equality; it is not a count directly comparable to individual list equality comparisons
n_a: the number of items in list a, here 10,000
n_b: the number of items in list b, here 10,000
≈: approximately equal to
In words: scanning a list for each item costs up to 100 million comparisons, while building a set once and looking items up in it costs about 20,000 operations.
```

These function definitions do not print anything. Both retain the order and duplicates from list a when values in b match; the set version changes lookup mechanics.

For the Django scenario, one query to fetch 300 orders followed by a separate customer lookup per order makes 301 queries. With a ForeignKey pointing to one related customer, `Order.objects.select_related("customer")` fetches the related customers using a join in the orders query. That queryset is an incomplete application example: it requires the actual model and database, and the one-query statement covers this access pattern only. Django many-to-many relationships instead need `prefetch_related`, normally adding a separate batched query. Query counts do not determine execution time: measure the joined or batched query too.

This is an asymptotic comparison, not a measured timing guarantee. It assumes stable, hashable values and effectively constant-time equality/hashing; the set uses extra memory proportional to the length of b (m in the code comments). Unhashable values or unusual equality semantics can invalidate this replacement. No universal seconds-to-milliseconds result is included because it cannot be reliably established without a specified workload and benchmark.

## Key takeaways
- Reduce unnecessary computation and round trips before tuning tiny operations.
- A set can replace repeated list scans for stable hashable values, at an extra memory cost.
- Average-case operation counts are not a measured speedup or a worst-case hash-table guarantee.

## Further reading
- [Python data model — hashing](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Django select_related and prefetch_related](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related)
