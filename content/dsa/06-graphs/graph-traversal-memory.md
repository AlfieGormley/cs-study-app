---
id: graph-traversal-memory
title: Traversal costs and iterative deepening
level: basic
minutes: 4
sourceLesson: graph-bfs-dfs
summary: Linear-time traversal requires adjacency lists and bounded vertex processing.
---

The running six-vertex undirected example has six edges: 0–1, 0–2, 1–3, 1–4, 2–4 and 4–5. Here n counts vertices, m counts edges, and deg(u) counts edges incident on vertex u. BFS uses a queue; DFS uses recursion or a stack.

## Complexity

With an adjacency list, BFS enqueues each vertex once, and both shown traversals scan each processed adjacency list once. The iterative DFS can push duplicates, but at most O(n + m) entries overall. Adding up the work per vertex gives the total:

```formula
W = n + Σ deg(u) = n + 2m
W = 6 + 2 × 6 = 18
O(n + m)
where
W: a work-accounting quantity: one vertex visit plus one adjacency-list entry read, over a full traversal of an undirected graph
n: the number of vertices; 6 in the example graph
m: the number of edges; 6 in the example graph
deg(u): the degree of vertex u: how many edges touch it, which is the length of its adjacency list
u: a vertex of the graph
Σ: sum over every vertex u
O(…): Big O: grows at most this fast, up to a constant factor
In words: you pay one step per vertex plus one per adjacency-list entry, and each undirected edge appears in two lists, so the total is n + 2m, which is O(n + m).
```

The "each edge counted twice" step is the handshake lemma: every undirected edge u–v appears once in u's list and once in v's. In the example graph the degrees of vertices 0 to 5 are 2, 3, 2, 1, 3 and 1, which add up to 12: twice its 6 edges. In a directed graph each edge appears once, giving n + m.

With an adjacency matrix, finding a vertex's neighbours means scanning its whole row of n cells, even if it has only one neighbour:

```formula
W = n^2
W = 1000^2 = 10^6
where
W: the total work of one traversal with an adjacency matrix, counted in matrix cells read
n: the number of vertices; 1000 in the example
In words: each of the n vertices scans a row of n cells, so the traversal costs O(n²) however few edges there are.
```

BFS and recursive DFS use O(n) auxiliary space. The displayed mark-on-pop iterative DFS can retain O(m) duplicate stack entries, so its bound is O(n + m). An explicit stack of active neighbour iterators can reproduce recursive DFS with O(n) auxiliary space. The frontier shapes below refer to tree search without retaining a global visited set:

| | BFS | DFS |
|---|---|---|
| Structure | Queue | Stack |
| Frontier memory | Exponential in depth | Linear in depth |
| Shortest path | Yes (unweighted) | No |
| Natural uses | Distances, layers | Cycles, ordering |

The frontier is the set of vertices discovered but not yet expanded. On a search tree where every vertex has the same number of children, the two traversals need very different amounts of frontier memory:

```formula
F_BFS ≈ b^d
F_DFS ≈ bd
F_BFS ≈ 10^6 and F_DFS ≈ 60
where
F_BFS: the number of vertices BFS holds in its queue when it reaches depth d
F_DFS: the number of vertices DFS holds on its stack (the current path plus the waiting siblings at each level)
b: the branching factor: how many children each vertex has; 10 in the example
d: the depth: how many levels below the start the search reaches; 6 in the example
≈: approximately equal to
In words: BFS's frontier grows exponentially with depth, because a whole layer sits in the queue, while DFS's grows only in proportion to depth.
```

With ten children per vertex and depth six, BFS holds about a million frontier vertices while DFS holds about sixty. The estimate assumes a full tree with no repeated states; on graphs with a visited set both still need memory for the set itself. That is why huge game-tree searches use DFS, or **iterative deepening** (DFS with depth limits 1, 2, 3, ...), which finds a shallowest goal with linear-depth search memory on finitely branching trees, using appropriate depth-limit handling.

## Key takeaways
- Linear-time traversal requires adjacency lists and bounded vertex processing.
- Separate frontier memory from a global visited set.
- Iterative deepening repeats shallow levels to reduce search-tree memory.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Breadth-first search — cp-algorithms](https://cp-algorithms.com/graph/breadth-first-search.html)
- [Iterative deepening depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
