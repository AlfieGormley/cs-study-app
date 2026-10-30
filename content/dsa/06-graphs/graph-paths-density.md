---
id: graph-paths-density
title: Paths, connectivity and graph density
level: basic
minutes: 3
sourceLesson: graph-fundamentals
summary: Distinguish walks, simple paths, cycles and connected trees.
---

A vertex is one entity; an edge joins two vertices. Here n counts vertices and m counts edges. This unit adds the words you need to describe routes through a graph and how crowded with edges it is.

### Weighted or unweighted

A **weighted graph** attaches a number to each edge: distance in km, latency in ms, cost in pounds, edge capacity in Mbit/s. Unweighted graphs treat every edge as cost 1. This distinction decides which shortest-path algorithm you can use (BFS for unweighted, Dijkstra and friends for weighted), because the choice of cost determines which path is cheapest.

### Paths, cycles and connectivity

- A **graph walk** follows a sequence of edges and may repeat vertices or edges. A **simple path** repeats no vertex; terminology for “path” varies, so this module says when repetitions matter.
- A **cycle** is a nonempty closed walk with no repeated vertices except its start/end and no repeated edges. In a simple undirected graph it has at least three edges: going along one edge and immediately back is not a cycle. A graph with no cycles is **acyclic**. A directed acyclic graph is a **DAG**, useful for prerequisite relations without circular dependencies.
- An undirected graph is **connected** if every vertex can reach every other. A connected acyclic undirected graph is a **tree**, and it always has exactly one edge fewer than it has vertices: a tree on 10 vertices has 9 edges.

### Dense or sparse

How many edges can a graph have at most? In a **simple** graph (no graph self-loops, no two edges joining the same pair), each edge is a different pair of distinct vertices. With 5 vertices there are 10 possible undirected edges, or 20 directed ones, because a one-way arrow can go each way between a pair.

```formula reference
m_max = n(n − 1) / 2
m_dir = n(n − 1)
where
n: the number of vertices
m_max: the maximum number of edges in a simple undirected graph
m_dir: the maximum number of edges in a simple directed graph
In words: the most edges a simple graph can have is every pair of vertices joined once, and twice that many if edges are one-way arrows; either way it grows roughly with the square of the vertex count.
```

So the maximum grows with the square of the vertex count: double the vertices and the possible edges roughly quadruple. A graph is **dense** if its edge count m is close to that maximum (on the order of n²) and **sparse** if m is closer to n.

Road maps are a familiar sparse example: a junction joins only a few roads, however large the map. Size alone makes the gap enormous. A hypothetical simple undirected graph with one billion vertices and an average of 200 edges per vertex has about 100 billion edges, against roughly 5 × 10¹⁷ possible pairs: about one in five million of the possible edges.

Density, required operations, mutability and memory layout all affect the representation choice, which the next two units compare.

## Key takeaways
- Distinguish walks, simple paths, cycles and connected trees.
- Count possible edges only after specifying direction and whether the graph is simple.
- The maximum edge count grows quadratically, so a large graph whose vertices each have only a few edges is very sparse.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Dense graph — Wikipedia](https://en.wikipedia.org/wiki/Dense_graph)
