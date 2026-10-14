---
id: graph-state-search-bidirectional
title: State-aware search and meeting in the middle
level: basic
minutes: 3
sourceLesson: graph-bfs-dfs
summary: Include keys, fuel or other move-dependent information in visited-state identity.
---

BFS finds fewest unit-cost moves. Its visited set records search states. A state must contain every fact needed to decide which next moves are legal.

## BFS over richer states

If the rules depend on more than your position, put that extra information **into the vertex**. In a maze with keys and locked doors, being at cell (3, 4) holding key A is a different situation from being there empty-handed.

So the state becomes `(row, col, keys)`, where `keys` is a bitmask: one bit per key, set to 1 if you hold it. The number of possible states is the number of cells times the number of key sets:

```formula
S = RC 2^K
S = 50 × 50 × 2^6
S = 2500 × 64 = 160000
where
S: the maximum number of distinct states (vertices of the state graph)
R: the number of grid rows; 50 here
C: the number of grid columns; 50 here
K: the number of different keys; 6 here
2^K: the number of possible sets of keys held, since each key is either held or not
In words: every cell can be visited once per combination of keys, so adding a key doubles the number of states.
```

So a 50 × 50 grid with 6 keys has at most 160,000 cell/key-set states; walls and reachability may reduce this. With 20 keys it would be over 2.6 billion, so this trick only suits a handful of keys. Assess memory for the chosen implementation. The same trick handles "you may break at most k walls" (state includes walls broken so far) or "move with remaining fuel f".

## Where these show up

- **Mark-and-sweep garbage collectors** mark live objects by traversing the reference graph from the roots (a multi-source traversal), then sweep whatever was not reached.
- **Web crawlers** traverse link graphs; their scheduling may use breadth-first ideas, priorities and per-site limits.
- **Degrees of separation** can be found with BFS. **Bidirectional BFS** searches from both ends; in directed graphs the backward search follows reversed edges. In a roughly tree-like model, two half-depth searches are much smaller than one full-depth search:

```formula
F_one ≈ b^d
F_two ≈ 2 × b^{d/2}
F_one ≈ 100^6 = 10^12
F_two ≈ 2 × 100^3 = 2 × 10^6
where
F_one: frontier vertices for one search from the start to depth d
F_two: frontier vertices for two searches, each going to depth d/2
b: the branching factor (average neighbours per vertex), greater than 1; 100 in the example
d: the length of the shortest path between the two people, in edges; 6 in the example
≈: approximately equal to
In words: meeting in the middle replaces one huge exponential with two much smaller ones, because b^d is b^{d/2} squared.
```

With 100 contacts each and six degrees of separation, that is about two million vertices instead of a trillion. Overlap between friend lists, degree variation and stopping rules affect actual work.

> [!note] Content gap
> No claim is made about LinkedIn’s current implementation: an authoritative implementation description was not verified.
- **Build tools and package managers** use DFS to walk dependency trees.

## Key takeaways
- Include keys, fuel or other move-dependent information in visited-state identity.
- Bidirectional search reverses edges on its backward side in a directed graph.
- Tree-like frontier estimates are modelling assumptions, not dataset benchmarks.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
