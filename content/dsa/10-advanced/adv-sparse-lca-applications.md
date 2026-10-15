---
id: adv-sparse-lca-applications
title: Sparse-table applications and update limits
level: advanced
minutes: 3
summary: An Euler-tour depth minimum gives a lowest common ancestor.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations.

### Where it is used

- **Lowest common ancestor**: record an Euler tour of a tree (the nodes visited by a DFS, including returns) and their depths. The LCA of u and v is the shallowest node between their first appearances: an RMQ. For a tree of n nodes (the tour records the root once and one entry for each outward and return edge traversal), that is O(n log n) build and O(1) per LCA.
- **Suffix arrays**: the longest common prefix of two distinct suffixes is the minimum of the LCP array between their positions, so an RMQ structure answers it in O(1).
- Very large static data: specialised micro/macro RMQ constructions combine small in-block tables with summaries of block minima to obtain O(n) build and O(1) query, where n is the array length. Whether the more specialised implementation is worthwhile depends on memory limits and workload; compare those costs before choosing it.

## Pitfalls

- Sparse tables on changing data: a point update can affect O(n) blocks across all levels, where n is the array length. Use a segment tree instead. The count adds up like this:

```formula
B_k ≤ 2^k
B ≤ 2^0 + 2^1 + … + 2^K = 2^{K+1} − 1
B ≤ 2^{K+1} − 1 < 2n
K = ⌊log_2(n)⌋
where
k: a row of the sparse table, holding blocks of length 2^k
B_k: how many blocks in row k contain the changed element
K: the top row number
B: the total number of entries that must be recomputed
n: the array length
2^k: k copies of 2 multiplied together
log_2(n): the base-2 logarithm of n
⌊ ⌋: floor: round down to the nearest whole number
≤: is at most
<: is less than
In words: each row has at most block-length many blocks covering the element, and those block lengths add up to less than twice n.
```

  For a million elements, the top row is nineteen. The geometric bound allows up to 1,048,575 affected entries, about a million, against roughly twenty nodes in a segment tree. This is an upper bound, not the exact number affected at any chosen position.
- **Using the overlap trick for sums**: it double-counts. The combine must be associative and idempotent.

## Key takeaways

- An Euler-tour depth minimum gives a lowest common ancestor.
- A point change can affect linearly many sparse-table entries.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
- [Farach-Colton and Bender’s specialised RMQ reduction](https://cp-algorithms.com/graph/lca_farachcoltonbender.html)
