---
id: disc-handshaking-degrees
title: "The handshaking lemma and degree counts"
level: intermediate
minutes: 3
summary: "Every undirected edge contributes two to the degree sum."
sourceLesson: disc-graphs
---

An undirected graph has vertices joined by edges. Its degree counts incident edge ends at a vertex: each loop contributes two. Count those ends to rule out impossible networks before constructing one.

### The handshaking lemma

Every edge has two ends, so if you add up the degrees of all the vertices, each edge is counted exactly twice. For multigraphs with loops, count each loop twice in the degree; then the same identity holds:

```formula
Σ deg(v) = 2 × m
2 + 2 + 2 = 2 × 3
where
Σ: "sum of": add up the expression after it once for every vertex v of the graph
deg(v): the degree of vertex v: the number of incident edge ends; a loop contributes two
v: a vertex of the graph
m: the number of edges
In words: the degrees add up to twice the number of edges. A triangle has three vertices of degree 2 and three edges, and 6 = 2 × 3.
```

Consequences you can use immediately:

- The degree sum is even, so the number of vertices with **odd degree is always even**.
- There is no graph on 7 vertices where every vertex has degree 3: the degree sum would be 7 × 3 = 21, which is odd, and the edge count would be 21 / 2 = 10.5.
- Dividing both sides by the number of vertices links edges to the average degree:

```formula
m = n × d / 2
m = 10^9 × 200 / 2 = 10^11
where
m: the number of edges
n: the positive number of vertices (the average degree needs a nonempty vertex set)
d: the average degree: the degree sum divided by n
In words: a graph's edge count is half of (vertices × average degree). A social network of a billion users averaging 200 friends has 100 billion friendship edges.
```

The handshaking lemma is about undirected edges. In a directed graph the same counting gives: the in-degrees add up to m, and so do the out-degrees.

## Key takeaways

- Every undirected edge contributes two to the degree sum.
- The number of odd-degree vertices is even; average degree determines total edge count.

## Further reading

- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
