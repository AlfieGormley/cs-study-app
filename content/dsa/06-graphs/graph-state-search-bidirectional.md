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

So the state becomes `(row, col, keys)`, where `keys` is a bitmask: one bit per key, set to 1 if you hold it. Two visits to the same cell with different keys are now different vertices, so BFS no longer wrongly treats the second visit as a repeat.

> [!analogy] Real-world analogy: an escape room
> In an escape room, standing by the locked cabinet with the brass key in your pocket is a very different situation from standing in the same spot empty-handed: different things are possible next.
>
> **How it maps:** your spot in the room is the grid cell, your pocket's contents are the key bitmask, and the pair is what the search treats as one vertex. "Have I been here before?" must compare both, or you would refuse to return to the cabinet once you had found the key.
>
> **Where it stops:** in a real room you also remember clues and partly solved puzzles. A search vertex must include every such fact that changes which moves are legal, and nothing else: adding irrelevant detail multiplies the number of states for no benefit.

The number of possible states is the number of cells times the number of key sets:

```formula reference
S = RC 2^K
where
S: the maximum number of distinct states (vertices of the state graph)
R: the number of grid rows
C: the number of grid columns
K: the number of different keys
2^K: the number of possible sets of keys held, since each key is either held or not
In words: every cell can be visited once per combination of keys, so each extra key doubles the number of possible states.
```

So a 50 × 50 grid with 6 keys has at most 160,000 cell/key-set states; walls and reachability may reduce this. With 20 keys it would be over 2.6 billion, so this trick only suits a handful of keys. Assess memory for the chosen implementation. The same trick handles "you may break at most k walls" (state includes walls broken so far) or "move with remaining fuel f".

## Where these show up

- **Mark-and-sweep garbage collectors** mark live objects by traversing the reference graph from all the roots at once, then sweep whatever was not reached.
- **Web crawlers** traverse link graphs; their scheduling may use breadth-first ideas, priorities and per-site limits.
- **Degrees of separation** can be found with BFS. **Bidirectional BFS** searches from both ends; in directed graphs the backward search follows reversed edges. In a roughly tree-like model, two half-depth searches are much smaller than one full-depth search:

```formula reference
F_one ≈ b^d
F_two ≈ 2 × b^{d/2}
where
F_one: frontier vertices for one search from the start to depth d
F_two: frontier vertices for two searches, each going to depth d/2
b: the branching factor (average neighbours per vertex), greater than 1
d: the length of the shortest path between the two people, in edges
≈: approximately equal to
In words: meeting in the middle replaces one search to the full depth with two searches to half that depth; each half-depth frontier is roughly the square root of the full-depth one, so together they are vastly smaller.
```

  With 100 contacts each and six degrees of separation, that is about two million vertices instead of a trillion. Overlap between friend lists, degree variation and stopping rules affect actual work.
- **Build tools and package managers** use DFS to walk dependency trees.

## Key takeaways
- Include keys, fuel or other move-dependent information in the state that the visited set records.
- Bidirectional search reverses edges on its backward side in a directed graph.
- Tree-like frontier estimates are modelling assumptions, not dataset benchmarks.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
