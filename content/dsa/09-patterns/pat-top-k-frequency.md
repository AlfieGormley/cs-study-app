---
id: pat-top-k-frequency
title: Count frequencies before selecting the leaders
level: advanced
minutes: 3
sourceLesson: pat-heaps
summary: A heap of scored items does not by itself count query frequencies.
---

Here n is the number of inputs, u is the number of distinct keys and k is a selection budget between one and u. Hashing is expected constant-cost; ties need a consistent policy.

## Frequency selection

The size-k heap works on a **stream of already scored items**: keeping the 100 largest numeric observations needs O(100) stored items. Exact top-100 query *frequencies* are different: frequencies must first be counted, which can require memory proportional to the number of distinct queries or external/distributed storage.

**Top-K frequent elements**: count with a `Counter` (expected O(n), O(u) entries for u distinct values), then take the top k by count with `heapq.nlargest(k, counts, key=counts.get)`. Since counts are bounded by n, a **bucket sort** (a list of buckets indexed by frequency) gets O(n) total.

## Exact leaders when counts exceed memory

A frequency table needs space for every distinct key, even if only a hundred leaders will be returned. Partition queries by a deterministic hash of the key across machines or files. Every occurrence of a key must reach the same partition. Count each partition exactly, select its local leaders with a size-budget min-heap, then select the global leaders from the union of local results.

The same total ranking must apply locally and globally: order first by frequency, then by a consistent key tie-breaker when the identity of tied results matters. A globally top-100 key cannot have a hundred better-ranked keys inside its own partition; if it did, it would not be globally top-100. Therefore the union of local top-100 results contains every global top-100 key.

Hash partitioning does not guarantee balanced distinct-key counts. Check partition sizes and repartition oversized groups or use external aggregation. A popular key can create large traffic while using only one counter; distinct-key count is a separate memory consideration. External sorting and counting groups is another exact approach that avoids loading all keys at once.

A Count-Min Sketch estimates frequencies but does not enumerate candidate keys by itself. A complete approximate heavy-hitter design needs candidate recovery plus error and probability parameters. This unit makes no turnkey accuracy claim for a sketch-plus-heap recipe.

## Key takeaways
- A heap of scored items does not by itself count query frequencies.
- Exact frequency counting retains one count per distinct key or uses external storage.
- Heap, sorting and frequency-bucket selection offer different time and space trade-offs.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
