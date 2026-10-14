---
id: graph-mst-clustering-tours
title: MST clustering, updates and tour bounds
level: intermediate
minutes: 3
sourceLesson: graph-mst
summary: MST paths do not minimise every source-to-target distance.
---

The running six-vertex example has MST edges A–C 1, B–C 2, D–E 2, E–F 3 and B–D 5, total 13. Its other edges are A–B 4, C–D 8, C–E 10 and D–F 6. A cut separates two non-empty vertex groups; a lightest crossing edge is safe to add. Here n counts vertices and m counts edges.

## Where MSTs are used

- **Network design**: cabling, pipelines, power grids (the problem Borůvka originally studied in 1926, for electrifying Moravia).
- **Single-linkage clustering**: run Kruskal but stop when k components remain (k is the number of clusters you want). For a complete graph of pairwise dissimilarities, the result is single-linkage clustering, maximising the minimum distance between clusters. On a sparse graph, spacing refers only to edges present in that graph.
- **Approximation algorithms**: doubling an MST and shortcutting repeated vertices gives a tour at most 2× optimal for metric TSP (where going direct is never longer than a detour). See the formula after this list.
- **Union-Find on its own**: incremental undirected connectivity, image segmentation, percolation simulations, and type unification in compilers.

The 2× bound for the travelling salesman problem comes from two inequalities:

```formula
L ≤ 2 W(MST) ≤ 2 L*
L ≤ 2 × 100 = 200
where
L: the length of the tour built from the doubled MST
MST: the minimum spanning tree
W(MST): tree total length, 100 kilometres here; the complete graph has non-negative metric distances
L*: the length of the best possible tour
≤: is at most
In words: walking round the tree uses each edge twice, shortcuts never add length, and any tour minus one edge is a spanning tree, so the MST is no heavier than the best tour.
```

So if the MST weighs 100 km, the tour is at most 200 km, and the best tour is at least 100 km.

## Pitfalls

- **MST is not a shortest-path tree.** The MST minimises total weight; the path between two vertices inside it can be much longer than their shortest path.
- **Directed graphs** need a minimum spanning *arborescence* (Chu–Liu/Edmonds' algorithm). Kruskal and Prim do not apply.
- **Disconnected input**: no spanning tree exists. Kruskal returns a minimum spanning forest; check `len(tree) == n - 1`.
- **Negative weights are fine.** Only the relative order of weights matters, unlike Dijkstra.

For a single edge-weight decrease, compare that edge with the heaviest edge on the unique tree path between its endpoints. If it is lighter, replacing that heaviest edge reduces the spanning-tree weight. This is the cycle exchange principle; the surrounding graph and its other weights are assumed unchanged.

## Key takeaways
- MST paths do not minimise every source-to-target distance.
- Stopping Kruskal early produces single-linkage clusters under the stated input assumptions.
- The doubled-tree tour bound requires metric distances.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/43mst/)
- [Minimum spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Minimum_spanning_tree)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Borůvka’s original 1926 paper](https://www.dml.cz/handle/10338.dmlcz/500114)
- [Nešetřil and Nešetřilová: MST history and original-paper translation](https://ems.press/content/book-files/27386)
