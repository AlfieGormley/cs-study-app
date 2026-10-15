---
id: adv-composite-invariants
title: Combining structures with invariants
level: intermediate
minutes: 2
summary: Choose one structure for each required operation.
sourceLesson: adv-designing-structures
---

Most "design a data structure" problems share one idea: **no single structure gives you every operation cheaply, so you glue two together**. Each structure covers the other's weakness, and the hard part is keeping them in sync.

Costs in this lesson are written in big-O notation, which says how the number of steps grows as the structure fills up. The card below defines the notation and shows what the gap means for a million items:

```formula
s_map = O(1)
s_walk = O(n)
s_walk ≈ n = 10^6
where
n: the number of items currently stored in the structure, e.g. the keys in a cache; here one million (10^6)
s_map: the steps for one hash-map lookup by key (expected, on average)
s_walk: the steps to find an item by walking a linked list, or to shift every later element along when deleting from the middle of an array (up to n in the worst case)
O(f): big-O notation: the step count grows no faster than f as n grows, ignoring constant factors; O(1) means a fixed number of steps however large n gets
≈: approximately equal to
In words: a hash-map lookup takes about the same few steps whether it holds ten keys or a million, while a walk or a shift can take about a million steps when there are a million items.
```

A hash map offers expected O(1) lookup but does not automatically maintain sorted-key or access-recency order. Python dictionaries do preserve insertion order. A linked list keeps order and can splice in O(1), but finding a node is O(n). An array gives O(1) access by position, but deleting from the middle is O(n). Combine them and you can often get O(1) for everything.

The method:

1. List the operations and the cost each must have.
2. For each operation, ask what it needs: lookup by key, an ordering, access by position?
3. Pick a structure for each need, and decide what the hash map's values point at (a node, an index).
4. Write down the **invariants** that tie them together, and check every operation preserves them.

Complexities below assume constant-time key hashing/equality and word-sized values. Hash operations are expected amortised O(1), and dynamic-array append/pop can resize; these are not worst-case per-operation guarantees.

## Key takeaways

- Choose one structure for each required operation.
- Write down the invariant joining the structures before implementing updates.

## Further reading
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [functools.lru_cache — Python docs](https://docs.python.org/3/library/functools.html)
- [LinkedHashMap — Java SE 21 API docs](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)
