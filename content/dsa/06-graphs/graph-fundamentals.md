---
id: graph-fundamentals
title: Graph fundamentals and representations
level: basic
minutes: 10
summary: Vertices, edges, direction and weight; adjacency lists, matrices and edge lists; and the implicit graphs hiding in grids and puzzles.
---

A **graph** is a set of things and the connections between them. The things are **vertices** (or nodes) and the connections are **edges**. Written formally, a graph is G = (V, E), and by convention n = |V| and m = |E|.

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

The **degree** counts incident edge ends; a self-loop contributes two. In a digraph we split it into **in-degree** (arrows in) and **out-degree** (arrows out). In an undirected graph the degrees sum to 2m, because every edge has two ends (the *handshake lemma*).

### Weighted or unweighted

A **weighted** graph attaches a number to each edge: distance in km, latency in ms, cost in pounds, capacity in Mbit/s. Unweighted graphs treat every edge as cost 1. This distinction decides which shortest-path algorithm you can use (BFS for unweighted, Dijkstra and friends for weighted).

### Paths, cycles and connectivity

- A **walk** follows a sequence of edges and may repeat vertices or edges. A **simple path** repeats no vertex; terminology for “path” varies, so this module states when repetitions matter.
- A **cycle** is a nonempty closed walk with no repeated vertices except its start/end and no repeated edges. In a simple undirected graph it has at least three edges: going along one edge and immediately back is not a cycle. A graph with no cycles is **acyclic**. A directed acyclic graph is a **DAG**, useful for prerequisite relations without circular dependencies.
- An undirected graph is **connected** if every vertex can reach every other. A connected acyclic undirected graph is a **tree**, and it always has exactly n − 1 edges.

### Dense or sparse

A simple undirected graph has at most n(n − 1)/2 edges; a simple digraph at most n(n − 1). A graph is **dense** if m is close to n² and **sparse** if m is closer to n.

For a hypothetical simple undirected graph with one billion vertices and average degree 200, the handshake lemma gives 10¹¹ edges, versus a maximum of about 5 × 10¹⁷. This is sparse.

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

- **Space:** O(n + m). Each undirected edge is stored twice, each directed edge once.
- **Iterate neighbours of u:** O(1 + deg(u)), which is exactly what BFS, DFS and Dijkstra need.
- **Is there an edge u→v?** O(1 + deg(u)) by scanning. Swap the inner lists for sets to make it O(1) on average.

This is the default for almost every algorithm in this module.

## Representation 2: adjacency matrix

For a simple unweighted graph, `M[u][v]` is 1 for an edge and 0 otherwise. For shortest-path weights, use infinity for absence so zero-weight edges remain distinguishable; initialise diagonal distances with the minimum of zero and any self-loop weight. A single cell cannot preserve multiple parallel-edge identities without additional data.

```
     0  1  2  3
 0 [ 0  1  1  0 ]
 1 [ 1  0  1  0 ]
 2 [ 1  1  0  1 ]
 3 [ 0  0  1  0 ]
```

An undirected graph gives a symmetric matrix.

- **Space:** O(n²), regardless of how many edges exist.
- **Edge lookup:** O(1), a single array index.
- **Iterate neighbours of u:** O(n), because you must scan the whole row, even if u has one neighbour.

> [!warning] The n² trap
> A matrix for 1,000,000 vertices has 10¹² cells. Even at one bit per cell that is about 125 GB. A packed CSR representation of 5 million undirected edges using 32-bit neighbour IDs and offsets needs about 44 MB for those arrays. A Python dictionary of lists has substantial additional object overhead.
>
> Content gap: no measured Python-memory footprint or traversal timing is supplied; the packed-array calculation is not a benchmark.

Matrices win for small or dense graphs, for algorithms built around them (Floyd–Warshall), and for linear algebra on graphs: for an unweighted adjacency matrix, the (u, v) entry of A^k counts length-k walks. PageRank instead iterates a normalised transition model with damping and handling for vertices without outgoing edges.

## Representation 3: edge list

Just a list of `(u, v)` or `(u, v, w)` tuples.

```python
edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2)]
```

- **Space:** O(m) for edges, plus any separately stored vertex set.
- Requires a full scan for "who are u's neighbours?" (O(m) scan).
- Perfect when an algorithm processes edges as a whole: **Kruskal's** MST sorts the edges, and **Bellman–Ford** relaxes every edge each round.

It is also how graphs usually arrive: a CSV of flights, a table of `follower_id, followee_id` rows. You read the edge list, then build whatever structure the algorithm needs.

## Comparison

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

A wall-free R × C grid has RC vertices and R(C − 1) + C(R − 1) undirected four-neighbour edges. Excluding walls gives at most those counts. Generating neighbours avoids storing predictable edges; precomputing them can still help some repeated workloads.

### State spaces

The vertices can be abstract **states**. In a sliding-tile puzzle, a state is a board arrangement and an edge is one legal move. In "word ladder" (turn COLD into WARM one letter at a time), a state is a word and an edge links words differing by one letter. In a lock with four dials, a state is a 4-digit combination with 8 neighbours (each dial up or down).

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
- **Parallel edges and self-loops.** Real data often contains duplicates. Decide whether they matter (they change degree counts and can break algorithms that assume a simple graph).
- **Recursion limits.** Python limits recursion depth (inspect `sys.getrecursionlimit()`); a sufficiently long path can raise `RecursionError`. Prefer iterative versions for large inputs.

## Key takeaways
- A graph is G = (V, E); n vertices, m edges. Edges can be directed and/or weighted.
- Adjacency lists use O(n + m) space and give O(deg u) neighbour iteration: a common choice for sparse graphs.
- Adjacency matrices use O(n²) space but give O(1) edge lookup: good for small, dense graphs and matrix algorithms.
- Edge lists suit algorithms that process all edges, such as Kruskal and Bellman–Ford.
- Many problems use implicit graphs (grids, puzzle states), where neighbours are generated on demand rather than stored.

## Further reading
- [Graph (abstract data type) — Wikipedia](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Adjacency matrix — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_matrix)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
- [Dense graph — Wikipedia](https://en.wikipedia.org/wiki/Dense_graph)
