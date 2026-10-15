---
id: disc-trees-forests-counts
title: "Trees, forests and labelled-tree counts"
level: intermediate
minutes: 3
summary: "A forest loses one component per cycle-free edge; a nonempty tree has one fewer edge than vertices."
sourceLesson: disc-graphs
---

## Trees

A **tree** is a connected graph with no cycles. Its edge count is fixed by its vertex count, and the same idea extends to a **forest** (a graph with no cycles that need not be connected, so it is a collection of separate trees):

```formula
m = n − 1
c = n − m
where
m: the number of edges
n: the number of vertices; a tree is nonempty, while an empty forest has zero vertices, edges and components
c: the number of components: separate connected pieces of the forest
In words: a tree on n vertices always has n − 1 edges, and a forest with n vertices and m edges falls into exactly n − m separate pieces. A tree is the forest with exactly one piece.
```

Why: start with n isolated vertices, which is n separate pieces. Adding an edge between two different pieces (which never creates a cycle) merges them, so the count drops by exactly one per edge. A 10-vertex tree therefore has 9 edges, and a 10-vertex forest with 7 edges has 3 components. This only holds when there are no cycles: an edge added inside a piece makes a cycle and does not reduce the count.

For a nonempty finite simple undirected graph with n vertices, these are equivalent:

1. It is connected and acyclic.
2. It is connected and has exactly n − 1 edges.
3. It is acyclic and has exactly n − 1 edges.
4. There is exactly one simple path between every pair of distinct vertices.

These equivalences are surprisingly handy. Adding an edge between previously nonadjacent vertices of a tree creates exactly one cycle; removing any edge disconnects it. The forest count is what Kruskal's algorithm and union-find exploit: each edge that joins two different components reduces the count by one.

A **spanning tree** of a connected graph is a tree that uses all its vertices. Network protocols (the Spanning Tree Protocol in Ethernet switching) build one to avoid broadcast loops. How many different trees can be built on a fixed set of labelled vertices is given by **Cayley's formula**:

```formula
T(n) = n^{n − 2}   for n ≥ 2
T(4) = 4^2 = 16
where
T(n): the number of different trees whose vertices are exactly the n labelled vertices (two trees differ if some pair is joined in one but not the other)
n: the number of vertices, at least 2
n^{n − 2}: n multiplied by itself n − 2 times
≥: is greater than or equal to
In words: there are n to the power n − 2 labelled trees on n vertices, so 4 labelled vertices can be joined into 16 different trees.
```

The 16 trees on four labelled vertices split into 4 stars (pick the centre) and 12 paths (the 24 orderings of the 4 vertices, halved because a path read backwards is the same tree). The count grows very fast: 10 vertices already allow 10⁸ trees. It counts labelled trees; if you ignore labels, 4 vertices only make 2 shapes (the star and the path).

## Key takeaways

- A forest loses one component per cycle-free edge; a nonempty tree has one fewer edge than vertices.
- Cayley’s formula counts labelled trees, so it differs from counting unlabelled shapes.

## Further reading

- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
