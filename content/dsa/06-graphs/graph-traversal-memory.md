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

With an adjacency list, BFS enqueues each vertex once, and both shown traversals scan each processed adjacency list once. The iterative DFS can push duplicates, but at most O(n + m) entries overall. Adding up the work per vertex gives the total: one step per vertex plus one per adjacency-list entry. Each undirected edge u–v appears once in u's list and once in v's (the handshake lemma), so the work is the vertex count plus twice the edge count. In the example graph the degrees of vertices 0 to 5 are 2, 3, 2, 1, 3 and 1, which add up to 12: twice its 6 edges, so a full traversal does 6 vertex visits plus 12 list reads. In a directed graph each edge appears once.

With an adjacency matrix, finding a vertex's neighbours means scanning its whole row of n cells, even if it has only one neighbour. Every one of the n vertices scans a row, so the traversal costs O(n²) however few edges there are: a thousand vertices means a million cell reads.

BFS and recursive DFS use O(n) auxiliary space. The displayed mark-on-pop iterative DFS can retain O(m) duplicate stack entries, so its bound is O(n + m). An explicit stack of active neighbour iterators can reproduce recursive DFS with O(n) auxiliary space. The frontier shapes below refer to tree search without retaining a global visited set:

| | BFS | DFS |
|---|---|---|
| Structure | Queue | Stack |
| Frontier memory | Exponential in depth | Linear in depth |
| Shortest path | Yes (unweighted) | No |
| Natural uses | Distances, layers | Cycles, ordering |

The frontier is the set of vertices discovered but not yet expanded. On a search tree where every vertex has the same number of children, the two traversals need very different amounts of frontier memory:

```formula reference
F_BFS ≈ b^d
F_DFS ≈ bd
where
F_BFS: the number of vertices BFS holds in its queue when it reaches depth d
F_DFS: the number of vertices DFS holds on its stack (the current path plus the waiting siblings at each level)
b: the branching factor: how many children each vertex has
d: the depth: how many levels below the start the search reaches
≈: approximately equal to
In words: BFS's frontier grows exponentially with depth, because a whole layer sits in the queue, while DFS's grows only in proportion to depth.
```

With ten children per vertex and depth six, BFS holds about a million frontier vertices while DFS holds about sixty. The estimate assumes a full tree with no repeated states; on graphs with a visited set both still need memory for the set itself. That is why huge game-tree searches use DFS, or **iterative deepening** (DFS with depth limits 1, 2, 3, ...), which finds a shallowest goal with linear-depth search memory on finitely branching trees, using appropriate depth-limit handling. It repeats the shallow levels, but in a bushy tree the deepest level holds most of the vertices, so the repetition adds little work.

> [!analogy] Real-world analogy: a search party versus one explorer
> To search a cave system level by level, a search party must post someone at every passage opening at the current depth before anyone goes deeper; with many branching passages the party soon needs thousands of people. A lone explorer trailing a ball of twine follows one passage at a time and only has to remember the turnings along the current route.
>
> **How it maps:** the people waiting at passage openings are BFS's queue, the frontier for a whole layer. The explorer's twine and remembered side turnings are DFS's stack: the current path plus the untried siblings at each level.
>
> **Where it stops:** a real explorer can see that two passages join up. A tree search with no visited set cannot, and on a graph both traversals still need memory for the set of visited vertices on top of their frontier.

## Key takeaways
- Linear-time traversal requires adjacency lists and bounded vertex processing.
- Separate frontier memory from a global visited set.
- Iterative deepening repeats shallow levels to reduce search-tree memory.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Breadth-first search — cp-algorithms](https://cp-algorithms.com/graph/breadth-first-search.html)
- [Iterative deepening depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
