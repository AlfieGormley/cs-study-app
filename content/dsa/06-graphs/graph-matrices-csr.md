---
id: graph-matrices-csr
title: Adjacency matrices and compact CSR storage
level: basic
minutes: 4
sourceLesson: graph-fundamentals
summary: Matrices trade quadratic storage for constant-time edge lookup.
---

Adjacency lists store neighbours explicitly; an adjacency matrix instead allocates a cell for each ordered pair. Here n counts vertices and m counts edges.

## Representation 2: adjacency matrix

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

> [!warning] The n² trap
> A matrix for 1,000,000 vertices has 10¹² cells. Even at one bit per cell that is about 125 GB. A packed CSR representation of 5 million undirected edges using 32-bit neighbour IDs and offsets needs about 44 MB for those arrays. A Python dictionary of lists has substantial additional object overhead.
>
> Content gap: no measured Python-memory footprint or traversal timing is supplied; the packed-array calculation is not a benchmark.

The two numbers in that warning come from these sums:

```formula
B_mat = (n^2 / 8) B
B_mat = ((10^6)^2 / 8) B
B_mat = 1.25 × 10^11 B
B_csr = (4(n + 1) + 8m) B
B_csr = (4 × 1000001 + 4 × 10^7) B
B_csr ≈ 4 MB + 40 MB = 44 MB
where
n: the number of vertices; 10^6 (a million) here
m: the number of undirected edges; 5 × 10^6 here, each stored twice in CSR
B_mat: bytes for a bit-packed adjacency matrix: one bit per cell, 8 bits per byte
B_csr: bytes for CSR: an offsets array of n + 1 entries and a neighbours array of 2 × m entries, 4 bytes each
B: byte, 8 bits
MB: megabyte, 10^6 bytes
In words: the matrix grows with the square of the vertex count whatever the edges, while CSR grows with vertices plus edges.
```

The bit-packed matrix needs about 125 GB (gigabytes), nearly 3,000 times the CSR array figure. A decimal gigabyte is one billion bytes. The matrix cost does not fall at all if the graph has few edges, which is why it only pays off when the graph is small or dense.

Matrices win for small or dense graphs, for algorithms built around them (Floyd–Warshall), and for linear algebra on graphs. Multiplying an unweighted adjacency matrix by itself counts walks:

```formula
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

For instance, if 0→1→0 and 0→2→0 are the only two-step round trips from vertex 0, the row-zero, column-zero entry of the squared matrix is two. PageRank instead iterates a normalised random-surfer model with damping and handling for vertices without outgoing edges.

## Real-world representations

- **Social and web graphs** at scale use compressed adjacency lists. **CSR** (compressed sparse row) stores all neighbour lists in one flat array plus an offsets array: neighbours of u are `nbrs[off[u]:off[u+1]]`. It is compact and cache-friendly, and is used by graph libraries and sparse-matrix code alike.
- **Graph databases** such as Neo4j keep relationship adjacency with nodes so traversals can follow connections without a global relationship lookup at every hop ("index-free adjacency"). The physical representation depends on the store format: record formats and newer block formats organise relationships differently. Degree, caching, store format and the query still affect traversal cost.
- **Routing engines** for road maps preprocess the graph heavily (contraction hierarchies) because millions of queries hit the same static graph.

## Key takeaways
- Matrices trade quadratic storage for constant-time edge lookup.
- Packed CSR sizes describe arrays, not Python object memory or measured speed.
- Matrix powers count walks, not necessarily simple paths.

## Further reading
- [Primary reference for this unit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html)
- [Adjacency matrix — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_matrix)
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Neo4j store formats](https://neo4j.com/docs/operations-manual/current/database-internals/store-formats/)
