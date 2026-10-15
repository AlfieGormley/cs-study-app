---
id: cplx-graph-complements
title: "Independent sets, covers and cliques"
level: intermediate
minutes: 4
summary: "Complementing a vertex set exchanges independent sets and covers."
sourceLesson: cplx-reductions
---

Continue with finite simple undirected graphs. Exact reductions connect three different graph questions; their decision thresholds use at least the requested independent/clique size and at most the requested cover size. A set of exactly the target independent size exists whenever a larger one does.

## Independent Set, Vertex Cover and Clique

A **vertex cover** is a set C of vertices touching every edge: every edge has at least one end in C. The key observation links it to independent sets:

```formula
S ∈ I(G)  iff  (V ∖ S) ∈ C(G)
f(G, k) = (G, n − k)
where
S: any set of vertices of the graph G
I(G): the collection of all independent sets of G (vertex sets with no edge inside them)
C(G): the collection of all vertex covers of G (vertex sets touching every edge)
∈: "is a member of"
G: the input graph, with vertex set V
V: the set of all vertices of G
∖: set difference: V ∖ S is every vertex of V that is not in S
n: the number of vertices in G
k: the independent-set size asked for
f: the reduction from Independent Set to Vertex Cover
f(G, k): the Vertex Cover instance it outputs: the same graph, with target size n − k
In words: a set is independent exactly when the vertices left over touch every edge, so asking for an independent set of size k is the same as asking for a vertex cover of size n − k.
```

Why the first line holds: if no edge has both ends in S, every edge has at least one end outside S, and vice versa. So the reduction doesn't even change the graph; it only changes the number. For example, a 10-vertex graph with an independent set of size 4 has a vertex cover of size 10 − 4 = 6.

A **clique** is a set of vertices all joined to each other. S is independent in G exactly when S is a clique in the **complement** graph Ḡ (same vertices, edges exactly where G has none):

```formula
f(G, k) = (Ḡ, k)
t_build = O(n^2)
where
G: the input graph
Ḡ: "G-bar", the complement graph: the same vertices as G, with an edge between two vertices exactly when G has no edge there
k: the target size, unchanged
f: the reduction from Independent Set to Clique
n: the number of vertices in G
t_build: the number of steps needed to build Ḡ
O(n^2): Big O: grows at most as fast as a constant times n squared, because Ḡ is built by checking each of the about n²/2 vertex pairs once
In words: to ask for an independent set of size k, ask for a clique of size k in the complement graph. Building the complement means visiting every pair of vertices, about n squared over 2 steps.
```

```
 G: 1-2, 2-3        complement: 1-3
 {1,3} independent  {1,3} a clique
 {2} covers both edges of G
```

An exhaustive audit checks the IS/VC equivalence for every vertex subset of every simple five-vertex graph. The complement argument above establishes the general statement.

For these decision maps the target is a nonnegative integer no larger than the vertex count. Out-of-range or malformed target encodings can be handled separately by a fixed yes- or no-instance as appropriate. The complement graph has no self-loops and considers only pairs of distinct vertices.

## Key takeaways

- Complementing a vertex set exchanges independent sets and covers.
- Complementing graph edges exchanges independent sets and cliques.
- The transformations run in polynomial time.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
