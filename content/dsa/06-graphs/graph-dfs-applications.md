---
id: graph-dfs-applications
title: Cycles, topological sort and SCCs
level: intermediate
minutes: 14
summary: Using DFS structure to detect cycles, order dependencies with Kahn's algorithm or DFS finish times, find strongly connected components with Tarjan or Kosaraju, and test bipartiteness.
---

Lesson 2 used DFS just to visit things. Its real power is the **structure** it leaves behind: which vertices are still "open" on the stack, and the order in which vertices finish. That structure answers questions such as "is there a circular dependency?", "in what order should I build these modules?" and "which pages all link to each other?".

## The three colours

Give every vertex a colour during DFS:

- **White**: not yet discovered.
- **Grey**: discovered, still on the recursion stack (we are somewhere inside its subtree).
- **Black**: finished; every vertex reachable from it has been explored.

When DFS at u looks at an edge u→v, the colour of v classifies the edge:

| v is | Edge type | Meaning |
|---|---|---|
| White | Tree edge | DFS goes to v |
| Grey | Back edge | v is u or an ancestor of u |
| Black | Forward or cross | Already done |

A back edge points from a vertex to one of its own ancestors, closing a loop. That gives the key theorem: **a directed graph has a cycle if and only if a DFS covering all vertices finds a back edge.**

## Cycle detection in directed graphs

```python
def has_cycle(n, adj):
    WHITE, GREY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def visit(u):
        color[u] = GREY
        for v in adj[u]:
            if color[v] == GREY:
                return True  # back edge
            if color[v] == WHITE:
                if visit(v):
                    return True
        color[u] = BLACK
        return False

    for u in range(n):
        if color[u] == WHITE and visit(u):
            return True
    return False
```

### Why "visited" is not enough

A plain visited set reports a cycle in this DAG, which has none:

```
    0
   / \
  v   v
  1   2
   \ /
    v
    3
```

DFS goes 0→1→3, finishes, then 0→2 finds 3 already visited. But 3 is black (finished), not grey. It is a cross edge, not a loop.

> [!warning] Grey, not visited
> Only grey means "on my current path". Checking `v in visited` instead of `color[v] == GREY` gives false positives on any DAG where two paths reconverge, such as the diamond above.

## Cycle detection in undirected graphs

In an undirected graph every edge appears in both directions, so from u you will always see your parent again. Ignore that one edge; any *other* already-visited neighbour closes a cycle.

```python
def has_cycle_undirected(n, adj):
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, -1)]
        while stack:
            u, parent = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, u))
                elif v != parent:
                    return True
    return False
```

Two shortcuts: a connected undirected graph is acyclic exactly when m = n − 1 (it is a tree), and Union-Find (lesson 6) detects a cycle the moment an edge joins two vertices already in the same set. The code is presented for simple undirected graphs. In a recursive multigraph DFS, distinguish the particular parent edge by *edge id*: ignoring every edge to the parent can hide a genuine two-edge cycle.

## Topological sort

A **topological order** of a DAG lists the vertices so that every edge u→v has u before v. For prerequisites, orient each edge from prerequisite to dependent: socks before shoes, shirt before tie. If edges instead point from a target to its dependencies, use reverse topological order. It exists **if and only if** the graph has no directed cycle, and there may be many valid orders.

Example DAG (A→C, B→C, B→D, C→E, D→E):

```
A ---> C ---> E
      ^      ^
     /      /
B ---> D ---
```

### Kahn's algorithm (BFS-style)

Repeatedly output a vertex with no remaining incoming edges, then delete its outgoing edges.

```python
from collections import deque

def kahn(n, adj):
    indeg = [0] * n
    for u in range(n):
        for v in adj[u]:
            indeg[v] += 1
    q = deque(u for u in range(n)
              if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) < n:
        return None  # cycle
    return order
```

On the example: in-degrees A0, B0, C2, D1, E2. The queue starts [A, B]. Output A (C→1), B (C→0, D→0), C (E→1), D (E→0), E. Order: **A, B, C, D, E**.

If a cycle exists, its vertices never reach in-degree 0, so the output is short. That makes Kahn's a cycle detector for free. Swap the queue for a min-heap to get the lexicographically smallest order.

### DFS-based

Run DFS and record each vertex when it **finishes**. A vertex finishes only after everything it points to has finished, so reversing the finish order puts every vertex before its successors.

```python
def topo_dfs(n, adj):
    seen, post = [False] * n, []

    def visit(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                visit(v)
        post.append(u)  # successors done

    for u in range(n):
        if not seen[u]:
            visit(u)
    return post[::-1]
```

On the example (starting from A): finish order E, C, A, D, B. Reversed: **B, D, A, C, E**. Different from Kahn's, and equally valid. (This version assumes a DAG; combine it with the grey check to detect cycles.)

Both run in **O(n + m)**.

| | Kahn's | DFS-based |
|---|---|---|
| Style | Queue, in-degrees | Recursion, finish order |
| Cycle check | Built in | Needs grey check |
| Parallelism | Shows ready tasks | No |
| Recursion | None | Deep on long chains |

> [!example] Where it is used
> Make, Bazel and Gradle order build steps topologically. Package managers order installs. Acyclic spreadsheet formulas can be recalculated in dependency order; circular formulas need error handling or an explicitly supported iterative calculation mode. Python ships `graphlib.TopologicalSorter`, a Kahn-style sorter whose `get_ready()` returns every task that can currently run in parallel.

## Strongly connected components

In a directed graph, u and v are **strongly connected** if each can reach the other. A **strongly connected component (SCC)** is a maximal set of mutually reachable vertices.

```
{0,1,2}:  0 -> 1 -> 2 -> 0
{3,4,5}:  3 -> 4 -> 5 -> 3
{6,7}:    6 -> 7 -> 6
between:  2 -> 3,  6 -> 5

condensation (a DAG):
[0,1,2] --> [3,4,5] <-- [6,7]
```

Edges: 0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3, 6→5, 6→7, 7→6. SCCs: **{0, 1, 2}**, **{3, 4, 5}**, **{6, 7}**.

Collapse each SCC to a single vertex and discard internal edges; you get the **condensation**, which is always a DAG. That is why SCCs matter: they turn any directed graph into a DAG of "clusters" you can topologically sort.

### Kosaraju's algorithm

1. DFS the whole graph, recording finish order.
2. Reverse every edge.
3. DFS the reversed graph, taking start vertices in **decreasing** finish time. Each tree found is one SCC.

Why it works: the vertex that finishes last lies in a "source" SCC of the condensation. In the reversed graph that SCC becomes a sink, so a DFS from it cannot leak into other components. Two passes, **O(n + m)**, and simple to get right.

### Tarjan's algorithm

One DFS pass. Each vertex gets an index `idx` (discovery order) and a `low` value: the smallest index reachable from its subtree using tree edges plus at most one edge to a vertex still on the SCC stack. This separate stack can include vertices whose recursive calls have already returned; it is not the grey recursion stack. Vertices are pushed onto a separate stack as discovered. When a vertex finishes with `low[u] == idx[u]`, it is the root of an SCC: pop the stack down to u.

```python
def tarjan(n, adj):
    idx = [None] * n
    low = [0] * n
    on_stack = [False] * n
    stack, sccs = [], []
    counter = 0

    def visit(u):
        nonlocal counter
        idx[u] = low[u] = counter
        counter += 1
        stack.append(u)
        on_stack[u] = True
        for v in adj[u]:
            if idx[v] is None:
                visit(v)
                low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], idx[v])
        if low[u] == idx[u]:  # root
            comp = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                comp.append(w)
                if w == u:
                    break
            sccs.append(comp)

    for u in range(n):
        if idx[u] is None:
            visit(u)
    return sccs
```

On the example it returns [5, 4, 3], then [2, 1, 0], then [7, 6]. Tarjan emits SCCs in **reverse topological order** of the condensation: sinks first. Also O(n + m), one pass, no reversed graph, but the `on_stack` check is easy to get wrong.

> [!tip] Uses of SCCs
> **2-SAT** is solved by building an implication graph and checking that no variable sits in the same SCC as its negation. Compilers find mutually recursive functions. Garbage collectors and dependency analysers find reference cycles.

## Bipartite check

An undirected graph is **bipartite** if its vertices split into two sides with every edge crossing between them: students and courses, jobs and machines. Equivalently, it can be **2-coloured** so no edge joins two vertices of the same colour.

Theorem: **a graph is bipartite if and only if it has no odd-length cycle.** A square (4-cycle) is bipartite; a triangle is not.

```python
def is_bipartite(n, adj):
    color = [None] * n
    for s in range(n):
        if color[s] is not None:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] is None:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
```

BFS colours by layer parity: even layers 0, odd layers 1. A clash means an edge inside one layer, or between two layers of equal parity, which closes an odd cycle. O(n + m), and the outer loop handles disconnected graphs.

## Pitfalls

- **Directed cycle detection with a visited set**: reports cycles in DAGs (the diamond).
- **Undirected logic on a directed graph** or vice versa: the parent trick is only for undirected graphs.
- **Recursion depth**: a sufficiently long chain can exceed Python’s configured recursion limit. Use iterative versions or `sys.setrecursionlimit` with care.
- **Forgetting disconnected parts**: every algorithm here needs the outer "for each unvisited vertex" loop.

## Key takeaways
- In DFS, an edge to a grey vertex (still on the stack) is a back edge; a directed graph is cyclic exactly when one exists.
- Undirected cycle detection ignores the edge back to the parent; any other visited neighbour closes a cycle.
- Topological order exists only for DAGs: Kahn's repeatedly removes in-degree-0 vertices; DFS reverses finish order. Both are O(n + m).
- SCCs are maximal mutually reachable sets; collapsing them gives a DAG. Kosaraju uses two passes and the reversed graph; Tarjan uses one pass with low-link values.
- A graph is bipartite iff it has no odd cycle, which BFS 2-colouring checks in O(n + m).

## Further reading
- [Topological sorting — Wikipedia](https://en.wikipedia.org/wiki/Topological_sorting)
- [Strongly connected component — Wikipedia](https://en.wikipedia.org/wiki/Strongly_connected_component)
- [Tarjan's strongly connected components algorithm — Wikipedia](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm)
- [Strongly connected components — cp-algorithms](https://cp-algorithms.com/graph/strongly-connected-components.html)
- [graphlib — Python docs](https://docs.python.org/3/library/graphlib.html)
- [Bipartite graph — Wikipedia](https://en.wikipedia.org/wiki/Bipartite_graph)
