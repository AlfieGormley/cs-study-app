---
id: tree-lca-preprocessing
title: Many ancestor queries with preprocessing
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: Binary lifting stores power-of-two ancestor jumps.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

### Many queries

For millions of LCA queries on a fixed tree of n nodes, each O(n) walk is too slow. Two standard upgrades:

- **Binary lifting**: precompute, for every node, its ancestors 1, 2, 4, 8, … levels up (see the table recurrence below), in O(n log n) time. Then lift the deeper node to the same depth and jump both up together in powers of two: O(log n) per query.
- **Euler tour + range minimum**: record a node and its depth on entry and again after returning from each child (not just DFS preorder); the LCA is the shallowest node between the first visits of p and q. With a sparse table, queries become O(1) after O(n log n) preprocessing. (Range-query structures such as segment and Fenwick trees are covered in the advanced module.)

The binary-lifting table is built from itself: two half-size jumps make one full-size jump. Give the root itself as its parent, or handle a missing-ancestor sentinel consistently, so upward jumps remain defined. The displayed level count applies to trees with at least two nodes; handle a one-node tree directly.

```formula
A_0(v) = P(v)
A_k(v) = A_{k−1}(A_{k−1}(v))
K = ⌈log_2(n)⌉
K = ⌈log_2(100000)⌉ = ⌈16.6⌉ = 17
where
v: any node
P(v): the parent of v
A_0(v): the ancestor 2^0 = 1 level above v, which is simply its parent
k: the table level, from 0 up to K − 1
A_k(v): the ancestor of v that is 2^k levels above it (k copies of 2 multiplied together: 1, 2, 4, 8, …)
A_{k−1}(v): the ancestor 2^(k−1) levels above v, from the previous level of the table
K: the number of table levels needed so a combination of jumps can cover any depth
n: the number of nodes, at least two for this level-count formula
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌈ ⌉: ceiling: round up to a whole number
In words: the ancestor 2^k levels up is the ancestor 2^(k−1) levels above the ancestor 2^(k−1) levels up, so each level of the table is built from the one before.
```

For 100,000 nodes that is 17 levels, 1.7 million table entries, and any climb of up to 99,999 levels takes at most 17 jumps (one per 1-bit in its binary form).

## Key takeaways
- Binary lifting stores power-of-two ancestor jumps.
- An Euler depth tour converts ancestor queries to range minima.
- Preprocessing pays off when a fixed tree serves many queries.

## Further reading
- [Lowest Common Ancestor (Euler tour) — cp-algorithms](https://cp-algorithms.com/graph/lca.html)
- [LCA with binary lifting — cp-algorithms](https://cp-algorithms.com/graph/lca_binary_lifting.html)
- [Euler tour technique — Wikipedia](https://en.wikipedia.org/wiki/Euler_tour_technique)
