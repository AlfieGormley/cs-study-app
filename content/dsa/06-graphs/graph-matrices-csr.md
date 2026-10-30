---
id: graph-matrices-csr
title: Adjacency matrices and compact CSR storage
level: basic
minutes: 4
sourceLesson: graph-fundamentals
summary: Matrices trade quadratic storage for constant-time edge lookup.
---

Adjacency lists store neighbours explicitly; an adjacency matrix instead allocates a cell for each ordered pair. Here n counts vertices and m counts edges.

## Adjacency matrix

For a simple unweighted graph, `M[u][v]` is 1 for an edge and 0 otherwise. For shortest-path weights, use infinity for absence so zero-weight edges remain distinguishable; initialise diagonal distances with the minimum of zero and any graph self-loop weight. A single cell cannot preserve multiple parallel-edge identities without additional data.

```
     0  1  2  3
 0 [ 0  1  1  0 ]
 1 [ 1  0  1  0 ]
 2 [ 1  1  0  1 ]
 3 [ 0  0  1  0 ]
```

An undirected graph gives a symmetric matrix. The matrix has n rows and n columns, where n is the number of vertices:

- **Space:** O(n²), regardless of how many edges exist.
- **Edge lookup:** O(1), a single array index.
- **Iterate neighbours of u:** O(n), because you must scan the whole row, even if u has one neighbour.

> [!analogy] Real-world analogy: the mileage chart in a road atlas
> Many road atlases print a triangular chart with every town along the top and down the side. To find the distance between two towns you read a single cell where the row and column meet.
>
> **How it maps:** towns are vertices and the cell for a pair is `M[u][v]`. Looking up one pair is instant, which is the matrix's O(1) edge test, and the chart's size grows with the square of the number of towns.
>
> **Where it stops:** a mileage chart fills every cell with a road distance, even for towns with no direct road. An adjacency matrix records only direct edges, so in a sparse graph most of its cells say "no edge", and a directed graph's matrix need not be symmetric, so you cannot print half of it.

> [!warning] The n² trap
> A matrix for 1,000,000 vertices has 10¹² cells. Even at one bit per cell that is about 125 GB (decimal gigabytes). A packed CSR representation (described below) of 5 million undirected edges, using 4-byte neighbour IDs and offsets, needs about 44 MB for its two arrays: about a million offsets plus 10 million neighbour entries, since each undirected edge is stored at both ends. A Python dictionary of lists adds substantial object overhead on top of the raw entries.

The matrix grows with the square of the vertex count whatever the edges, while list-style storage grows with vertices plus edges. The matrix cost does not fall at all if the graph has few edges, which is why it only pays off when the graph is small or dense. These are sizes of packed arrays, not measured memory or speed.

Matrices win for small or dense graphs, for algorithms built around them (Floyd–Warshall), and for linear algebra on graphs. For example, multiplying an unweighted adjacency matrix by itself counts walks:

```formula reference
W_k(u, v) = (A^k)[u][v]
where
A: the adjacency matrix: entry [u][v] is 1 if there is an edge u→v, else 0
k: a walk length, in edges (1, 2, 3, …)
A^k: k copies of A multiplied together (matrix multiplication)
u: the start vertex (a row of the matrix)
v: the end vertex (a column)
W_k(u, v): the number of different walks of exactly k edges from u to v
In words: the entry in row u, column v of the k-th power of the adjacency matrix is the number of k-step walks from u to v.
```

For instance, if 0→1→0 and 0→2→0 are the only two-step walks that leave vertex 0 and return to it, the row-zero, column-zero entry of the squared matrix is two. These are walks, which may repeat vertices, not simple paths. PageRank instead iterates a normalised random-surfer model with damping and handling for vertices without outgoing edges.

## Real-world representations

- **Social and web graphs** at scale use compressed adjacency lists. **CSR** (compressed sparse row) stores all neighbour lists in one flat array plus an offsets array: neighbours of u are `nbrs[off[u]:off[u+1]]`. It is compact and cache-friendly, and is used by graph libraries and sparse-matrix code alike.
- **Graph databases** such as Neo4j keep relationship adjacency with nodes so traversals can follow connections without a global relationship lookup at every hop ("index-free adjacency"). The physical representation depends on the store format: record formats and newer block formats organise relationships differently. Degree, caching, store format and the query still affect traversal cost.
- **Routing engines** for road maps preprocess the graph heavily (contraction hierarchies) because millions of queries hit the same static graph.

## Key takeaways
- Matrices trade quadratic storage for constant-time edge lookup.
- Packed CSR sizes describe arrays, not Python object memory or measured speed.
- Matrix powers count walks, not necessarily simple paths.

## Further reading
- [SciPy docs: scipy.sparse.csr_matrix](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html)
- [Adjacency matrix — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_matrix)
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Neo4j store formats](https://neo4j.com/docs/operations-manual/current/database-internals/store-formats/)
