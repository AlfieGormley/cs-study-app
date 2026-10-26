---
id: disc-handshaking-degrees
title: "The handshaking lemma and degree counts"
level: intermediate
minutes: 2
summary: "Every undirected edge contributes two to the degree sum."
sourceLesson: disc-graphs
---

An undirected graph has vertices joined by edges. Its degree counts incident edge ends at a vertex: each loop contributes two. Count those ends to rule out impossible networks before constructing one.

### The handshaking lemma

Every edge has two ends, so if you add up the degrees of all the vertices, each edge is counted exactly twice. For multigraphs with loops, count each loop twice in the degree; then the same identity holds:

```formula essential
Σ deg(v) = 2 × m
where
Σ: "sum of": add up the expression after it once for every vertex v of the graph
deg(v): the degree of vertex v: the number of incident edge ends; a loop contributes two
v: a vertex of the graph
m: the number of edges
In words: Adding all vertex degrees counts every undirected edge twice, once for each end, including both ends of a self-loop.
```

Consequences you can use immediately:

- The degree sum is even, so the number of vertices with **odd degree is always even**.
- Seven vertices of degree three would give an odd degree sum. That is impossible: edge ends must occur in pairs.

The average degree determines the total number of edge ends. Halve that total to count edges. This assumes undirected links and counts a self-loop twice; it does not describe follower counts in a directed network.

In a directed graph, the in-degrees add up to the edge count, and the out-degrees separately add up to that same count.

## Key takeaways

- Every undirected edge contributes two to the degree sum.
- The number of odd-degree vertices is even; average degree determines total edge count.

## Further reading

- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
