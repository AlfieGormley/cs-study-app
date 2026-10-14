---
id: graph-paths-density
title: Paths, connectivity and graph density
level: basic
minutes: 3
sourceLesson: graph-fundamentals
summary: Distinguish walks, simple paths, cycles and connected trees.
---

A vertex is one entity; an edge joins two vertices. Here n counts vertices and m counts edges. Weighted edges attach a cost to a connection; the choice of cost determines which path is cheapest.

### Weighted or unweighted

A **weighted graph** attaches a number to each edge: distance in km, latency in ms, cost in pounds, edge capacity in Mbit/s. Unweighted graphs treat every edge as cost 1. This distinction decides which shortest-path algorithm you can use (BFS for unweighted, Dijkstra and friends for weighted).

### Paths, cycles and connectivity

- A **Walk (graph)** follows a sequence of edges and may repeat vertices or edges. A **simple path** repeats no vertex; terminology for “path” varies, so this module specifies when repetitions matter.
- A **cycle** is a nonempty closed walk with no repeated vertices except its start/end and no repeated edges. In a simple undirected graph it has at least three edges: going along one edge and immediately back is not a cycle. A graph with no cycles is **acyclic**. A directed acyclic graph is a **DAG**, useful for prerequisite relations without circular dependencies.
- An undirected graph is **connected** if every vertex can reach every other. A connected acyclic undirected graph is a **tree**, and it always has exactly one edge fewer than it has vertices: a tree on 10 vertices has 9 edges.

### Dense or sparse

How many edges can a graph have at most? In a **simple** graph (no graph self-loops, no two edges joining the same pair), each edge is a different pair of distinct vertices, so counting pairs gives the ceiling:

```formula
m_max = n(n − 1) / 2
m_dir = n(n − 1)
m_max = 5 × 4 / 2 = 10
where
n: the number of vertices
m_max: maximum undirected edge count
m_dir: maximum directed edge count
In words: in an undirected graph every unordered pair of vertices can have at most one edge; in a directed graph each pair can have one arrow each way, which doubles the count.
```

The worked line is a five-vertex undirected graph: at most 10 edges (20 if directed). Both maxima grow like n², n multiplied by itself. A graph is **dense** if its edge count m is close to n² and **sparse** if m is closer to n.

For a hypothetical simple undirected graph with one billion vertices and an average degree of 200, the handshake lemma gives the edge count, which is tiny next to the maximum:

```formula
m = n d_avg / 2
m = 10^9 × 200 / 2 = 10^11
m_max = 10^9 × (10^9 − 1) / 2 ≈ 5 × 10^17
where
n: the number of vertices; 10^9 (one billion) here
d_avg: the average degree of a vertex; 200 here
m: the number of edges
m_max: the largest possible number of edges in a simple undirected graph with n vertices
≈: approximately equal to
In words: a billion vertices with 200 edges each has 100 billion edges, only about one in five million of the possible pairs.
```

This is sparse.

> [!note] Content gap
> Population-wide claims about typical road or social graph degrees are omitted because no specified dataset and measurement support them here.

Density, required operations, mutability and memory layout all affect the representation choice.

## Key takeaways
- Distinguish walks, simple paths, cycles and connected trees.
- Count possible edges only after specifying direction and whether the graph is simple.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Dense graph — Wikipedia](https://en.wikipedia.org/wiki/Dense_graph)
