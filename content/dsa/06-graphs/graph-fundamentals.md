---
id: graph-fundamentals
title: Graph fundamentals and representations
level: basic
minutes: 10
summary: Vertices, edges, direction and weight; adjacency lists, matrices and edge lists; and the implicit graphs hiding in grids and puzzles.
---

A **graph** is a set of things and the connections between them. The things are **vertices** (or nodes) and the connections are **edges**. Textbooks write a graph as a pair of two sets, and name the two sizes that every running time in this module is measured in:

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

For example, a map of four towns joined by five roads has n = 4 and m = 5. Every cost in this module, such as O(n + m), is stated in terms of these two numbers.

Graphs are everywhere once you look: road networks, social networks, package dependencies, web links, flight routes, the states of a Rubik's cube. A huge number of problems become easy once you notice "this is a graph" and reach for a standard algorithm.

## The vocabulary

### Directed or undirected

In an **undirected** graph an edge {u, v} goes both ways: friendship on Facebook, a two-way street. In a **directed** graph (a *digraph*) an edge (u, v) goes from u to v only: following on X, a one-way street, "module A imports module B".

```
undirected        directed
 A --- B           A --> B
 |     |           ^     |
 |     |           |     v
 C --- D           C <-- D
```

In the undirected graph, every vertex can reach every other. In the directed one, A reaches B, D and C, and C reaches A, so here everything is mutually reachable too, but only because the arrows happen to form a loop.

The **degree** counts incident edge ends; a graph self-loop (an edge from a vertex back to itself) contributes two. In a digraph we split it into **in-degree** (arrows in) and **out-degree** (arrows out).

Adding up every vertex's degree counts each edge twice, once from each end. This is the *handshake lemma*, and it lets you get the edge count from the degrees (or the other way round):

```formula
Σ_v deg(v) = 2 × m
m = (3 + 3 + 2 + 2 + 2) / 2 = 6
where
v: any one vertex of the graph
deg(v): the degree of v: how many edge ends touch it
Σ_v: add up the following quantity over every vertex v
m: the number of edges in the graph
In words: in an undirected graph the degrees add up to exactly twice the number of edges, because every edge has two ends.
```

The worked line is a five-vertex graph with degrees 3, 3, 2, 2 and 2: the sum is 12, so it has 6 edges. A consequence: the degree sum is always even, so no graph has degrees 3, 2, 2. In a directed graph the version is different: the in-degrees add up to m, and so do the out-degrees, because each arrow has one tail and one head.

### Weighted or unweighted

A **weighted** graph attaches a number to each edge: distance in km, latency in ms, cost in pounds, capacity in Mbit/s. Unweighted graphs treat every edge as cost 1. This distinction decides which shortest-path algorithm you can use (BFS for unweighted, Dijkstra and friends for weighted).

### Paths, cycles and connectivity

- A **walk** follows a sequence of edges and may repeat vertices or edges. A **simple path** repeats no vertex; terminology for “path” varies, so this module states when repetitions matter.
- A **cycle** is a nonempty closed walk with no repeated vertices except its start/end and no repeated edges. In a simple undirected graph it has at least three edges: going along one edge and immediately back is not a cycle. A graph with no cycles is **acyclic**. A directed acyclic graph is a **DAG**, useful for prerequisite relations without circular dependencies.
- An undirected graph is **connected** if every vertex can reach every other. A connected acyclic undirected graph is a **tree**, and it always has exactly one edge fewer than it has vertices: a tree on 10 vertices has 9 edges.

### Dense or sparse

How many edges can a graph have at most? In a **simple** graph (no graph self-loops, no two edges joining the same pair), each edge is a different pair of distinct vertices, so counting pairs gives the ceiling:

```formula
m_max = n × (n − 1) / 2
m_max = n × (n − 1)
m_max = 5 × 4 / 2 = 10
where
n: the number of vertices
m_max: the largest possible number of edges; the first line is for a simple undirected graph, the second for a simple directed graph
In words: in an undirected graph every unordered pair of vertices can have at most one edge; in a directed graph each pair can have one arrow each way, which doubles the count.
```

The worked line is a five-vertex undirected graph: at most 10 edges (20 if directed). Both maxima grow like n², n multiplied by itself. A graph is **dense** if its edge count m is close to n² and **sparse** if m is closer to n.

For a hypothetical simple undirected graph with one billion vertices and an average degree of 200, the handshake lemma gives the edge count, which is tiny next to the maximum:

```formula
m = n × d_avg / 2
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

## Representation 1: adjacency list

For each vertex, store a list of its neighbours. In Python, a dict of lists (or a list of lists when vertices are numbered 0..n−1).

```
graph:  0 - 1, 0 - 2, 1 - 2, 2 - 3

adj = {
  0: [1, 2],
  1: [0, 2],
  2: [0, 1, 3],
  3: [2],
}
```

```python
def build_adj(vertices, edges,
              directed=False):
    adj = {v: [] for v in vertices}
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return adj
```

Pass every vertex explicitly, including isolates and directed sinks; each edge endpoint must belong to that set. Complexity assumes constant-size labels and expected O(1) dictionary/set operations. For a weighted graph, store pairs: `adj[u].append((v, w))`.

The memory is one slot per vertex plus one list entry per edge end:

```formula
S = n + 2 × m
S = 4 + 2 × 4 = 12
where
S: the number of stored items (dictionary keys plus list entries) in an undirected adjacency list
n: the number of vertices
m: the number of edges; each undirected edge is stored in both endpoints' lists
In words: the storage grows with the vertex count plus twice the edge count; for a directed graph it is n + m.
```

The example above has 4 vertices and 4 edges: 4 keys plus 2 + 2 + 3 + 1 = 8 list entries, 12 in all. In the costs below, n is the number of vertices, m the number of edges and deg(u) the degree of vertex u. O(…) is Big O notation: how the cost grows as the graph grows, ignoring constant factors.

- **Space:** O(n + m). Each undirected edge is stored twice, each directed edge once.
- **Iterate neighbours of u:** O(1 + deg(u)), which is exactly what BFS, DFS and Dijkstra need.
- **Is there an edge u→v?** O(1 + deg(u)) by scanning. Replace the inner lists with sets to make it O(1) on average.

This is the default for almost every algorithm in this module.

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
B_mat = n^2 / 8
B_mat = (10^6)^2 / 8 B = 1.25 × 10^11 B
B_csr = 4 × (n + 1) + 4 × 2 × m
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

1.25 × 10^11 bytes is about 125 GB (gigabytes, 10^9 bytes each), nearly 3,000 times the CSR figure. The matrix cost does not fall at all if the graph has few edges, which is why it only pays off when the graph is small or dense.

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

For instance, if 0→1→0 and 0→2→0 are the only two-step round trips from vertex 0, the [0][0] entry of A^2 is 2. PageRank instead iterates a normalised random-surfer model with damping and handling for vertices without outgoing edges.

## Representation 3: edge list

Just a list of `(u, v)` or `(u, v, w)` tuples.

```python
edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2)]
```

Here m is the number of edges.

- **Space:** O(m) for edges, plus any separately stored vertex set.
- Requires a full scan for "who are u's neighbours?" (O(m) scan).
- Perfect when an algorithm processes edges as a whole: **Kruskal's** MST sorts the edges, and **Bellman–Ford** relaxes every edge each round.

It is also how graphs usually arrive: a CSV of flights, a table of `follower_id, followee_id` rows. You read the edge list, then build whatever structure the algorithm needs.

## Comparison

As before, n is the number of vertices, m the number of edges and deg u the degree of vertex u.

| Operation | List | Matrix | Edges |
|---|---|---|---|
| Space | O(n + m) | O(n²) | O(m) |
| Edge u→v? | O(1 + deg u) | O(1) | O(m) |
| Neighbours | O(1 + deg u) | O(n) | O(m) |
| Add edge | O(1) amortised | O(1) | O(1) amortised |

Traversing all vertices costs O(n + m) with adjacency lists and O(n²) with a matrix. A traversal from one source scans only reachable vertices; the displayed bounds are whole-graph upper bounds. These are growth rates, not measured elapsed times.

## Implicit graphs

Often the graph is never stored at all. You have a rule that, given a vertex, generates its neighbours on demand. This is an **implicit graph**.

### Grids

A maze or image is a grid where each cell is a vertex and neighbours are the adjacent cells.

```
grid       neighbours of (1,1)
S . #           (0,1)
. . .     (1,0) (1,1) (1,2)
# . E           (2,1)
```

```python
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def neighbours(grid, r, c):
    # Precondition: rectangular grid.
    if not grid or not grid[0]:
        return
    R, C = len(grid), len(grid[0])
    if not (0 <= r < R and 0 <= c < C):
        return
    if grid[r][c] == "#":
        return
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if (0 <= nr < R and 0 <= nc < C
                and grid[nr][nc] != '#'):
            yield nr, nc
```

You can count a grid's size without building it. Each row has one link fewer than it has cells, and so does each column:

```formula
n = R × C
m = R × (C − 1) + C × (R − 1)
n = 3 × 3 = 9
m = 3 × 2 + 3 × 2 = 12
where
R: the number of rows in the grid
C: the number of columns
n: the number of vertices (cells)
m: the number of undirected edges when you can move up, down, left or right
In words: a wall-free grid has one vertex per cell, and each row and each column contributes one edge fewer than its length.
```

The worked lines are the 3 × 3 grid above with its walls removed: 9 cells and 12 edges. Walls only remove vertices and edges, so a grid with walls has at most those counts. Since m is about 2 × n for large grids, grids are sparse. Generating neighbours avoids storing predictable edges; precomputing them can still help some repeated workloads.

### State spaces

The vertices can be abstract **states**. In a sliding-tile puzzle, a state is a board arrangement and an edge is one legal move. In "word ladder" (turn COLD into WARM one letter at a time), a state is a word and an edge links words differing by one letter. In a lock with four dials, a state is a 4-digit code with 8 neighbours (each dial up or down).

State spaces can be astronomically large: the 15-puzzle has about 10¹³ reachable states. Search often generates states as needed; even then exhaustive BFS can be infeasible. BFS, DFS and A* can use a `neighbours(state)` function instead of stored adjacency.

> [!tip] Spotting a graph problem
> Ask: "What are the states, and what moves take me from one to another?" If the answer is clear, you have a graph. BFS minimises the number of unit-cost moves when the reachable search space is manageable.

## Real-world representations

- **Social and web graphs** at scale use compressed adjacency lists. **CSR** (compressed sparse row) stores all neighbour lists in one flat array plus an offsets array: neighbours of u are `nbrs[off[u]:off[u+1]]`. It is compact and cache-friendly, and is used by graph libraries and sparse-matrix code alike.
- **Graph databases** such as Neo4j store each node with direct pointers to its relationships ("index-free adjacency"), avoiding a global relationship lookup for each traversal. Degree, storage layout, caching and the query still affect traversal cost.
- **Routing engines** for road maps preprocess the graph heavily (contraction hierarchies) because millions of queries hit the same static graph.

## Pitfalls

- **Forgetting the reverse edge** in an undirected graph: add both `adj[u].append(v)` and `adj[v].append(u)`, or some intended paths may be lost.
- **Isolated vertices** vanish from an adjacency dict built only from edges. If vertex 7 has no edges, it never appears, and a "count components" loop will undercount. Initialise all n vertices first.
- **Parallel edges and graph self-loops.** Real data often contains duplicates. Decide whether they matter (they change degree counts and can break algorithms that assume a simple graph).
- **Recursion limits.** Python limits recursion depth (inspect `sys.getrecursionlimit()`); a sufficiently long path can raise `RecursionError`. Prefer iterative versions for large inputs.

## Key takeaways
- A graph is a set of vertices plus a set of edges; n counts the vertices and m the edges. Edges can be directed and/or weighted.
- Adjacency lists use O(n + m) space and give O(1 + deg u) neighbour iteration, where deg u is the degree of u: a common choice for sparse graphs.
- Adjacency matrices use O(n²) space but give O(1) edge lookup: good for small, dense graphs and matrix algorithms.
- Edge lists suit algorithms that process all edges, such as Kruskal and Bellman–Ford.
- Many problems use implicit graphs (grids, puzzle states), where neighbours are generated on demand rather than stored.

## Further reading
- [Graph (abstract data type) — Wikipedia](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Adjacency matrix — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_matrix)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
- [Dense graph — Wikipedia](https://en.wikipedia.org/wiki/Dense_graph)
