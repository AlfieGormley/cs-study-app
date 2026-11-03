---
id: adv-composite-invariants
title: Combining structures with invariants
level: intermediate
minutes: 2
summary: Choose one structure for each required operation.
sourceLesson: adv-designing-structures
---

Most "design a data structure" problems share one idea: **no single structure gives you every operation cheaply, so you glue two together**. Each structure covers the other's weakness, and the hard part is keeping them in sync.

Here n is the number of stored items. Big-O describes how work grows with n, ignoring constant factors: O(1) stays bounded as the structure grows, while O(n) can grow in proportion to its size.

A hash map offers expected O(1) lookup but does not automatically maintain sorted-key or access-recency order. Python dictionaries do preserve insertion order. A linked list keeps order and can splice in O(1), but finding a node is O(n). An array gives O(1) access by position, but deleting from the middle is O(n). Combine them and you can often get O(1) for everything.

The method:

1. List the operations and the cost each must have.
2. For each operation, ask what it needs: lookup by key, an ordering, access by position?
3. Pick a structure for each need, and decide what the hash map's values point at (a node, an index).
4. Write down the **invariants** that tie them together, and check every operation preserves them.

> [!analogy] Real-world analogy: A cloakroom register
> A cloakroom keeps both a ticket register and an ordered rail of coats.
>
> **How it maps:** The register finds a coat by ticket, while the rail keeps an ordering. Removing a coat requires updating both records, just as a composite structure must keep its map and list in agreement.
>
> **Where it stops:** A physical rail does not provide constant-time pointer changes; the comparison explains agreement between representations, not their running times.

These complexity claims assume constant-time key hashing/equality and word-sized values. Hash operations are expected amortised O(1), and dynamic-array append/pop can resize; these are not worst-case per-operation guarantees.

## Key takeaways

- Choose one structure for each required operation.
- Write down the invariant joining the structures before implementing updates.

## Further reading
- [CPython’s LRU cache implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Lib/functools.py)
- [Python ordered dictionaries](https://docs.python.org/3/library/collections.html)
- [Redis cache eviction policies](https://redis.io/docs/latest/develop/reference/eviction/)
