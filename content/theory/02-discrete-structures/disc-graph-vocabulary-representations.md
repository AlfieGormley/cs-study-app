---
id: disc-graph-vocabulary-representations
title: "Graph vocabulary and representations"
level: intermediate
minutes: 4
summary: "A graph records vertices and their connections, with direction and multiplicity stated explicitly."
sourceLesson: disc-graphs
---

A **graph** is a set of things and the connections between them. Road networks, the web, social networks, package dependencies, chip layouts, the call graph of a program and the interference between variables in a compiler are all graphs. The DSA subject covers graph *algorithms* (BFS, Dijkstra, and so on). This lesson is about the *theory*: the facts that tell you what is possible before you write any code, and which problems have efficient general algorithms and which have no known polynomial-time solution.

## Vocabulary

A graph is made of **vertices** (the things, also called nodes) and **edges** (the connections). In an **undirected** graph an edge just joins two vertices, with no direction; in a **directed graph** it points from one vertex to another. A **simple graph** has no self-loops (an edge from a vertex to itself) and no repeated edges. Unless stated otherwise, "graph" here means simple and undirected. Textbooks write all this in a compact notation that the rest of the module uses:

```formula essential
G = (V, E)
{u, v} ∈ E
(u, v) ∈ E
n = |V|
m = |E|
where
G: the graph, a pair made of a vertex set and an edge set
V: the set of vertices
E: the set of edges
u, v: two vertices of the graph
{u, v}: an undirected edge: an unordered pair, so {u, v} and {v, u} are the same edge
(u, v): a directed edge: an ordered pair, pointing from u to v, so reversing different endpoints changes the direction
∈: "is an element of", so {u, v} ∈ E says that this edge is one of the graph's edges
|V|, |E|: the size of a set: how many elements it has
n: the number of vertices
m: the number of edges
In words: a graph G is a set of vertices V plus a set of edges E; an undirected edge is an unordered pair of vertices, a directed edge an ordered pair, and n and m count the vertices and edges.
```

A triangle has three vertices and three edges, one for each unordered pair.

- The **degree of a vertex** v, written deg(v), is the number of edges touching it. In the triangle every vertex has degree 2.
- A walk is a sequence of vertices joined by edges. A simple path repeats no vertex; a cycle closes a path by returning to its start, with no other repeated vertices. An Euler trail may revisit vertices but never edges.
- A **connected graph** has a path between every pair of vertices.
- The **complete graph** Kₙ has an edge between every pair of its n vertices.

For a complete graph, each vertex connects to every other vertex. Counting those neighbours at every vertex counts each undirected edge twice. The total number of edges therefore grows quadratically with the vertex count.

### Representations

Here n counts vertices, m counts edges, u is the queried vertex, and deg u means its degree. Big-O gives an upper bound on growth up to constant factors.

| | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | O(n + m) | O(n²) |
| Is u–v an edge? | O(deg u) | O(1) |
| List neighbours | O(deg u) | O(n) |
| Good for | Sparse graphs | Dense graphs |

For sparse graphs, adjacency lists avoid reserving a cell for every possible pair. The table assumes unsorted neighbour lists; hash-set or sorted representations change membership costs.

## Key takeaways

- A graph records vertices and their connections, with direction and multiplicity stated explicitly.
- Adjacency lists and matrices trade space against edge-query and neighbour-enumeration costs.

## Further reading

- [Tree (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
