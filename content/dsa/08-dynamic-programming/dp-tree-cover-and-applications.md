---
id: dp-tree-cover-and-applications
title: Tree covers, rerooting and interval applications
level: advanced
minutes: 2
summary: Excluding a vertex forces every child into a vertex cover.
sourceLesson: dp-interval-tree
---

### Other tree DPs with the same shape

- **Tree diameter**: for each node, the two longest downward paths through different children.
- **Minimum vertex cover** (the fewest nodes such that every edge touches at least one of them): the same two states, with min instead of max.

```formula
inc[v] = 1 + Σ min(inc[c], exc[c])
exc[v] = Σ inc[c]
where
inc[v]: the smallest cover of v's subtree that includes v (the 1 counts v itself)
exc[v]: the smallest cover of v's subtree that leaves v out
v: a node
c: each child of v; Σ adds over all of them (0 for a leaf)
Σ: sum over v's children
min: the smaller of the two values
In words: if v is in the cover, each child edge is already covered and the child may do whatever is cheaper; if v is out, every child must be in to cover the edge to v.
```

- **Rerooting**: for suitable constant-sized states and O(1)-per-edge combination/exclusion (often using prefix/suffix aggregates), a second top-down pass can compute every root’s answer in O(n). More expensive transitions change the bound.

## In the real world

- **Parsing**: CYK uses an interval DP for a grammar in Chomsky normal form, in O(n³ · |G|) time for a nonempty string of n words, where |G| is the size (number of rules) of the grammar; handle an allowed empty string separately.
- **RNA secondary structure** prediction in noncrossing base-pair models (such as Nussinov and Zuker formulations) uses interval DP; unrestricted pseudoknots need other treatment.
- **Optimal binary search trees** (given access frequencies) are interval DP; Knuth's observation that the optimal root index is monotone cuts it from O(n³) to O(n²) for n keys.
- **Compilers** use tree DP for instruction selection: tiling an expression tree with machine instructions at minimum cost.

## Key takeaways
- Excluding a vertex forces every child into a vertex cover.
- Rerooting is linear only with suitably cheap state combination.
- Parsing, RNA models, search trees and instruction selection use related DPs.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
