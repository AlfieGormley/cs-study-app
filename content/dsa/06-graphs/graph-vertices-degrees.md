---
id: graph-vertices-degrees
title: Vertices, edge direction and degrees
level: basic
minutes: 3
sourceLesson: graph-fundamentals
summary: Vertices identify entities; edges identify their connections.
---

A **graph** is a set of things and the connections between them. The things are **vertices** (also called nodes) and the connections are **edges**. A map with four towns and five roads is a graph with four vertices and five edges.

Two counts matter throughout this module: n is the number of vertices and m is the number of edges. Textbooks often call the graph G, its set of vertices V and its set of edges E. Every running time in this module, such as O(n + m), is stated in terms of n and m. O(…) is Big O notation: how the cost grows as the graph grows, ignoring constant factors.

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

In the undirected graph, every vertex can reach every other. In the directed one, A reaches B, D and C, and C reaches A, so here everything is mutually reachable too, but only because the arrows happen to form a loop. Reverse one arrow and that stops being true.

### Degree

The **vertex degree** counts the edge ends touching a vertex. A graph self-loop (an edge from a vertex back to itself) has both ends at the same vertex, so it adds two. In a digraph we split degree into **in-degree** (arrows in) and **out-degree** (arrows out).

Adding up every vertex's degree counts each edge exactly twice, once from each end. This is the *handshake lemma*:

```formula essential
Σ_v deg(v) = 2m
where
v: any one vertex of the graph
deg(v): the degree of v: how many edge ends touch it
Σ_v: add up the following quantity over every vertex v
m: the number of edges in the graph
In words: in an undirected graph the degrees add up to exactly twice the number of edges, because every edge has two ends.
```

It lets you move between degrees and edges. A five-vertex graph with degrees 3, 3, 2, 2 and 2 has a degree sum of 12, so it has 6 edges. It also catches impossible data: the degree sum is always even, so no graph has degrees 3, 2 and 2, and a degree list with an odd total has been recorded wrongly.

> [!analogy] Real-world analogy: counting handshakes at a party
> After a party, everyone says how many hands they shook. Add up all the answers and you get twice the number of handshakes, because every handshake involved two people and was reported by both.
>
> **How it maps:** guests are vertices, handshakes are undirected edges and each guest's answer is their degree. The total of the answers is the degree sum, which is twice the edge count.
>
> **Where it stops:** a guest cannot shake their own hand, but a graph can have a graph self-loop, which adds two to one vertex's degree. And in a directed graph, such as "who sent a party invitation to whom", each arrow has one sender and one receiver: the in-degrees add up to m and so do the out-degrees, separately.

In a directed graph the version is different for exactly that reason: each arrow has one tail and one head, so the in-degrees add up to m, and so do the out-degrees.

## Key takeaways
- Vertices identify entities; edges identify their connections.
- Count edge ends to recover undirected edge counts.
- An odd degree total means the data is inconsistent.

## Further reading
- [NetworkX docs: Graph](https://networkx.org/documentation/stable/reference/classes/graph.html)
- [Handshaking lemma — Wikipedia](https://en.wikipedia.org/wiki/Handshaking_lemma)
