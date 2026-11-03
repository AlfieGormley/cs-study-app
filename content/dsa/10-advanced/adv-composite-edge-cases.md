---
id: adv-composite-edge-cases
title: Composite designs and concurrent access
level: intermediate
minutes: 2
summary: Match lookup, ordering and sampling needs to complementary structures.
sourceLesson: adv-designing-structures
---

## Recognising the pattern

| Need | Structure |
|---|---|
| Find by key | Hash map |
| Recency or insertion order | Doubly linked list |
| Uniform random / by index | Dynamic array |
| Min or max, changing | Heap |
| Sorted order, ranges | Balanced BST |

Other classics built the same way:

- **Min stack**: a stack of `(value, min so far)` pairs gives O(1) `get_min`.
- **Time-based key-value store**: map from key to a list of `(timestamp, value)` appended in time order, then binary search, for O(log n) "value at time t", where n is the number of timestamps stored for that key and t is the time asked about.
- **All O(1) data structure** (increment, decrement, get max key, get min key): the LFU bucket idea, with a doubly linked list of count buckets.

## Pitfalls

- Forgetting one side. A common bug is the two structures drifting apart: a key left in the map after its node was evicted, or an index pointing at a moved element.
- Average, not worst case. The O(1) relies on hash map operations being O(1) on average. Adversarial keys can degrade them.
- **Capacity edge cases.** Capacity 0, updating an existing key when full (no eviction should happen), and removing the last element are where interview solutions break.
- **Concurrency.** A cache-hit `get` on this LRU implementation writes recency pointers. Concurrent access needs a correct synchronisation strategy, commonly a lock around operations; a miss does not move a node. This is one reason high-throughput caches approximate LRU instead.

## Key takeaways

- Match lookup, ordering and sampling needs to complementary structures.
- Capacity limits and concurrent recency writes must preserve every structure together.

## Further reading
- [CPython’s LRU cache implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/functools.py)
- [Python ordered dictionaries](https://docs.python.org/3/library/collections.html)
- [Redis cache eviction policies](https://redis.io/docs/latest/develop/reference/eviction/)
