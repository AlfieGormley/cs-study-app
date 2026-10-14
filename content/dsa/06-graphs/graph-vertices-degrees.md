---
id: graph-vertices-degrees
title: Vertices, edge direction and degrees
level: basic
minutes: 3
sourceLesson: graph-fundamentals
summary: Vertices identify entities; edges identify their connections.
---

A **graph** is a set of things and the connections between them. The things are **vertices** (also called nodes) and the connections are **edges**. Textbooks write a graph as a pair of two sets, and name the two sizes that every running time in this module is measured in:

```formula
G = (V, E)
n = |V|
m = |E|
where
G: the graph
V: the set of its vertices (the things)
E: the set of its edges (the connections), each joining two vertices
|V|: the size of the set V: how many vertices there are
|E|: the size of the set E: how many edges there are
n: shorthand for the number of vertices
m: shorthand for the number of edges
( , ): a pair: G is made of V and E together
In words: a graph is its vertices plus its edges; n counts the vertices and m counts the edges.
```

For example, a map can have four towns and five roads. Every cost in this module, such as O(n + m), is stated in terms of these two numbers.

Graphs are everywhere once you look: road networks, social networks, package dependencies, web links, flight routes, the states of a Rubik's cube. A huge number of problems become easy once you notice "this is a graph" and reach for a standard algorithm.

## The vocabulary

### Directed or undirected

In an **undirected** graph an edge {u, v} goes both ways: friendship on Facebook, a two-way street. In a **directed graph** (a *digraph*) an edge (u, v) goes from u to v only: following on X, a one-way street, "module A imports module B".

```
undirected        directed
 A --- B           A --> B
 |     |           ^     |
 |     |           |     v
 C --- D           C <-- D
```

In the undirected graph, every vertex can reach every other. In the directed one, A reaches B, D and C, and C reaches A, so here everything is mutually reachable too, but only because the arrows happen to form a loop.

The **vertex degree** counts incident edge ends; a graph self-loop (an edge from a vertex back to itself) contributes two. In a digraph we split it into **in-degree** (arrows in) and **out-degree** (arrows out).

Adding up every vertex's degree counts each edge twice, once from each end. This is the *handshake lemma*, and it lets you get the edge count from the degrees (or the other way round):

```formula
Σ_v deg(v) = 2m
m = (3 + 3 + 2 + 2 + 2) / 2 = 6
where
v: any one vertex of the graph
deg(v): the degree of v: how many edge ends touch it
Σ_v: add up the following quantity over every vertex v
m: the number of edges in the graph
In words: in an undirected graph the degrees add up to exactly twice the number of edges, because every edge has two ends.
```

The worked line is a five-vertex graph with degrees 3, 3, 2, 2 and 2: the sum is 12, so it has 6 edges. A consequence: the degree sum is always even, so no graph has degrees 3, 2, 2. In a directed graph the version is different: the in-degrees add up to m, and so do the out-degrees, because each arrow has one tail and one head.

## Key takeaways
- Vertices identify entities; edges identify their connections.
- Count edge ends to recover undirected edge counts.

## Further reading
- [Primary reference for this unit](https://networkx.org/documentation/stable/reference/classes/graph.html)
- [Handshaking lemma — Wikipedia](https://en.wikipedia.org/wiki/Handshaking_lemma)
