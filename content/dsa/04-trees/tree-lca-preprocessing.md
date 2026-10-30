---
id: tree-lca-preprocessing
title: Many ancestor queries with preprocessing
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: Binary lifting stores power-of-two ancestor jumps.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

## Many queries

For millions of LCA queries on a fixed tree of n nodes, each O(n) walk is too slow. Two standard upgrades:

- **Binary lifting**: precompute, for every node, its ancestors 1, 2, 4, 8, … levels up, in O(n log n) time. Then lift the deeper node to the same depth and jump both up together in powers of two: O(log n) per query.
- **Euler tour + range minimum**: record a node and its depth on entry and again after returning from each child (not just DFS preorder); the LCA is the shallowest node between the first visits of p and q. With a sparse table, queries become O(1) after O(n log n) preprocessing. (Range-query structures such as segment and Fenwick trees are covered in the advanced module.)

The binary-lifting table is built from itself: two half-size jumps make one full-size jump. The ancestor 8 levels up is the ancestor 4 levels above the ancestor 4 levels up, so each level of the table comes from the one before. Give the root itself as its parent, or handle a missing-ancestor sentinel consistently, so upward jumps remain defined.

```formula reference
A_k(v) = A_{k−1}(A_{k−1}(v))
where
v: any node
k: the table level, from 1 upwards; level 0 holds each node's parent
A_k(v): the ancestor of v that is 2^k levels above it (k copies of 2 multiplied together: 2, 4, 8, …)
A_{k−1}(v): the ancestor 2^(k−1) levels above v, from the previous level of the table
In words: each jump stored in the table is two jumps of half that size from the level before, so the whole table is built level by level from the parents.
```

For 100,000 nodes that is 17 levels and 1.7 million table entries. Any climb of up to 99,999 levels is split into powers of two, like writing the number in binary: a climb of 13 is 8 + 4 + 1, three jumps. So no climb needs more than 17 jumps.

> [!analogy] Real-world analogy: express lifts in a tall building
> A tower has lifts that go up 1, 2, 4, 8 or 16 floors at a time. To go up 13 floors you take the 8, then the 4, then the 1: three rides instead of thirteen stops.
>
> **How it maps:** floors are levels in the tree, each express lift is one level of the binary-lifting table, and choosing lifts by the binary digits of the distance is how a query climbs. The LCA query lifts the deeper node to the other's level, then takes the biggest jumps that keep both nodes below their common ancestor.
>
> **Where it stops:** a building shares one set of lifts. The table stores a separate set of jumps for every node, which is why it costs memory in proportion to the number of nodes times the number of levels, and it must be rebuilt if the tree changes.

## Key takeaways
- Binary lifting stores power-of-two ancestor jumps.
- An Euler depth tour converts ancestor queries to range minima.
- Preprocessing pays off when a fixed tree serves many queries.

## Further reading
- [Lowest Common Ancestor (Euler tour) — cp-algorithms](https://cp-algorithms.com/graph/lca.html)
- [LCA with binary lifting — cp-algorithms](https://cp-algorithms.com/graph/lca_binary_lifting.html)
- [Euler tour technique — Wikipedia](https://en.wikipedia.org/wiki/Euler_tour_technique)
