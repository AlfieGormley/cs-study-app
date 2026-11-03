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

- **Lowest common ancestor**: record an Euler tour of a tree (the nodes visited by a DFS, including returns) and their depths. The LCA of u and v is the shallowest node between their first appearances: an RMQ. For a tree of n nodes (the DFS walk records the root once and one entry for each outward and return edge traversal), that is O(n log n) build and O(1) per LCA.
- Store the DFS-walk position or node identity with each depth minimum. A numeric depth minimum alone does not identify which node to return.
- **Suffix arrays**: the longest common prefix of two distinct suffixes is the minimum of the LCP array between their positions, so an RMQ structure answers it in O(1).
- Very large static data: specialised micro/macro RMQ constructions combine small in-block tables with summaries of block minima to obtain O(n) build and O(1) query, where n is the array length. Whether the more specialised implementation is worthwhile depends on memory limits and workload; compare those costs before choosing it.

## Pitfalls

- Sparse tables on changing data: a point update can affect O(n) stored blocks across levels, where n is array length. Many blocks with different starts include the changed position. A segment tree stores a fixed partition at each level, so a point update changes only one node per level. Use that structure for frequent updates.

- **Using the overlap trick for sums**: it double-counts. The combine must be associative and idempotent.

## Key takeaways

- The minimum depth on an Euler tour identifies a lowest common ancestor.
- A point change can affect linearly many sparse-table entries.

## Further reading
- [Farach-Colton and Bender’s specialised RMQ reduction](https://cp-algorithms.com/graph/lca_farachcoltonbender.html)
- [Lowest common ancestors via DFS — cp-algorithms](https://cp-algorithms.com/graph/lca.html)
- [Sparse tables — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
