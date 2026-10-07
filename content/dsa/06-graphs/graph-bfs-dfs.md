---
id: graph-bfs-dfs
title: BFS and DFS
level: basic
minutes: 12
summary: The two fundamental traversals, how visited sets keep them linear, and how they give you components, flood fill and unweighted shortest paths.
---

Almost every graph algorithm is a traversal in disguise. There are two basic ways to explore a graph from a starting vertex:

- **Breadth-first search (BFS)** spreads out like a ripple in a pond: first everything 1 step away, then everything 2 steps away, and so on.
- **Depth-first search (DFS)** behaves like someone in a maze with a ball of string: go as deep as possible down one corridor, and only back up when you hit a dead end.

With adjacency lists and the usual constant-time access model, both process every reachable vertex once in O(n + m) time. Dictionary/set bounds here are expected bounds. All referenced vertices must have adjacency entries. What differs is the *order*, and that order is what makes each one useful.

We will use this graph throughout:

```
0 --- 1 --- 3
|     |
2 --- 4 --- 5

adj = {0: [1, 2], 1: [0, 3, 4],
       2: [0, 4], 3: [1],
       4: [1, 2, 5], 5: [4]}
```

## Breadth-first search

BFS uses a **queue** (first in, first out). Start by enqueuing the source. Repeatedly dequeue a vertex and enqueue any neighbours you have not seen yet.

```python
from collections import deque

def bfs(adj, s):
    dist = {s: 0}
    parent = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return dist, parent
```

Here `dist` doubles as the visited set. Tracing from 0:

| Dequeue | Enqueue | Queue after |
|---|---|---|
| 0 | 1, 2 | [1, 2] |
| 1 | 3, 4 | [2, 3, 4] |
| 2 | (none new) | [3, 4] |
| 3 | (none) | [4] |
| 4 | 5 | [5] |
| 5 | (none) | [] |

Visit order: 0, 1, 2, 3, 4, 5. Distances: 0→0, 1→1, 2→1, 3→2, 4→2, 5→3.

### Why BFS finds shortest paths

The queue always holds vertices from at most two consecutive layers: some at distance d, then some at d + 1. So BFS finishes every vertex at distance d before touching any at d + 1. The first time BFS reaches a vertex, it has reached it by the fewest possible edges.

BFS always minimises edge count. This also minimises total cost when all edges have the same non-negative cost. For unequal non-negative weights use Dijkstra; negative weights require additional care (lesson 4).

To recover the actual path, follow `parent` pointers back from the target and reverse:

```python
def path_to(parent, t):
    if t not in parent:
        return None
    path = []
    while t is not None:
        path.append(t)
        t = parent[t]
    return path[::-1]

# path_to(parent, 5) -> [0, 1, 4, 5]
```

### Mark when you enqueue, not when you dequeue

> [!warning] A classic bug
> If you mark a vertex visited only when it is *dequeued*, it can be enqueued many times by different neighbours before it is processed. On a dense graph the queue can grow to O(m) entries, and some versions compute wrong distances. Mark (or set `dist`) at the moment you enqueue.

## Depth-first search

DFS uses a **stack**, either the call stack (recursion) or an explicit list.

```python
def dfs(adj, u, seen):
    seen.add(u)
    for v in adj[u]:
        if v not in seen:
            dfs(adj, v, seen)
```

From 0 the recursive version visits 0, 1, 3, 4, 2, 5. It dives 0→1→3, hits a dead end, backs up to 1, goes to 4, then 2 (whose neighbours are all seen), backs up to 4, then 5.

```
dfs(0)
 └ dfs(1)
    ├ dfs(3)
    └ dfs(4)
       ├ dfs(2)
       └ dfs(5)
```

The iterative version avoids Python's configurable recursion-depth limit, which a long chain easily exceeds:

```python
def dfs_iter(adj, s):
    seen, order = set(), []
    stack = [s]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        for v in adj[u]:
            if v not in seen:
                stack.append(v)
    return order
```

This one visits 0, 2, 4, 5, 1, 3. It is still a valid DFS, but the order differs because the *last* neighbour pushed is popped first. Push neighbours in reverse if you need the recursive order. Note that here the `seen` check happens on pop, so a vertex may sit on the stack more than once; that is fine and still O(n + m) overall.

## Complexity

With an adjacency list, BFS enqueues each vertex once, and both shown traversals scan each processed adjacency list once. The iterative DFS can push duplicates, but at most O(n + m) entries overall. Total work is n + Σ deg(u) = n + 2m for an undirected graph: **O(n + m)**.

With an adjacency matrix, scanning a vertex's neighbours costs n, so it becomes **O(n²)**.

BFS and recursive DFS use O(n) auxiliary space. The displayed mark-on-pop iterative DFS can retain O(m) duplicate stack entries, so its bound is O(n + m). An explicit stack of active neighbour iterators can reproduce recursive DFS with O(n) auxiliary space. The frontier shapes below refer to tree search without retaining a global visited set:

| | BFS | DFS |
|---|---|---|
| Structure | Queue | Stack |
| Frontier memory | O(b^d) on a full tree | O(bd) with pending siblings |
| Shortest path | Yes (unweighted) | No |
| Natural uses | Distances, layers | Cycles, ordering |

On a tree with branching factor b and depth d, BFS may hold about b^d vertices in its frontier, whereas DFS holds only about b × d. That is why huge game-tree searches use DFS, or **iterative deepening** (DFS with depth limits 1, 2, 3, ...), which finds a shallowest goal with linear-depth search memory on finitely branching trees, using appropriate depth-limit handling.

## Connected components

A traversal from s finds everything reachable from s. To find *every* component of an undirected graph, loop over all vertices and start a new traversal from each unvisited one.

```python
def components(n, adj):
    seen = set()
    count = 0
    for v in range(n):
        if v not in seen:
            count += 1
            dfs(adj, v, seen)
    return count
```

Total work is still O(n + m): each vertex and edge is handled once across all traversals. (In a directed graph this gives "reachability trees", not strongly connected components; see lesson 3.)

## Flood fill

Flood fill is a traversal on a grid: the paint-bucket tool, or "count the islands". Each land cell is a vertex; edges join adjacent land cells.

```
grid      islands
##..#     AA..B
#...#     A...B
..#..     ..C..
....#     ....D
```

That grid has 4 islands. The code is the components loop over cells, with a 4-direction neighbour function (lesson 1). Use an explicit stack or BFS: a recursive flood fill on a 1000 × 1000 image can recurse a million deep.

## Multi-source BFS

Sometimes you want each vertex's distance to the *nearest* of several sources: the nearest exit, the nearest hospital, how many minutes until every orange in a crate rots.

Running BFS from every source separately costs k × O(n + m). Instead, **put all sources in the queue at distance 0** and run one BFS.

```python
def nearest(adj, sources):
    dist = {s: 0 for s in sources}
    q = deque(dist)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

```
grid (E = exit)   distance to nearest E
E . . .           0 1 2 2
. # # .           1 # # 1
. . . E           2 2 1 0
```

It works because it is equivalent to adding a virtual super-source joined to every real source by an edge, then doing ordinary BFS and subtracting one from every real vertex’s distance. The layers still expand in order.

## BFS over richer states

If the rules depend on more than your position, put that extra information **into the vertex**. In a maze with keys and locked doors, being at cell (3, 4) holding key A is a different situation from being there empty-handed.

So the state becomes `(row, col, keys)`, where `keys` is a bitmask. With a 50 × 50 grid and 6 keys there are at most 2,500 × 2⁶ = 160,000 cell/key-set states; walls and reachability may reduce this. Assess memory for the chosen implementation. The same trick handles "you may break at most k walls" (state includes walls broken so far) or "move with remaining fuel f".

## Where these show up

- **Mark-and-sweep garbage collectors** mark live objects by traversing the reference graph from the roots (a multi-source traversal), then sweep whatever was not reached.
- **Web crawlers** traverse link graphs; their scheduling may use breadth-first ideas, priorities and per-site limits.
- **Degrees of separation** can be found with BFS. **Bidirectional BFS** searches from both ends; in directed graphs the backward search follows reversed edges. In a roughly tree-like model with branching factor b > 1, searching depth d/2 from each end suggests about 2b^(d/2) rather than b^d frontier vertices. Overlap, degree variation and stopping rules affect actual work.

> [!note] Content gap
> No claim is made about LinkedIn’s current implementation: an authoritative implementation description was not verified.
- **Build tools and package managers** use DFS to walk dependency trees.

## Pitfalls

- **Forgetting the visited set** on a graph with cycles: the traversal loops forever.
- **Using DFS for "fewest steps".** DFS finds *a* path, not the shortest.
- **`list.pop(0)` as a queue** is O(n) per pop in Python. Use `collections.deque`.
- **Missing disconnected parts.** A single traversal only covers one component.

## Key takeaways
- BFS uses a queue and explores in layers; in an unweighted graph the first visit to a vertex is via a shortest path.
- DFS uses a stack (or recursion) and goes deep first; it is the basis for cycle detection and ordering.
- Both are O(n + m) with an adjacency list (O(n²) with a matrix) and need a visited set to avoid loops.
- Mark vertices visited when you enqueue them, not when you dequeue them.
- Components and flood fill are "traverse from every unvisited vertex"; multi-source BFS starts with every source in the queue.

## Further reading
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-first search — cp-algorithms](https://cp-algorithms.com/graph/breadth-first-search.html)
- [Depth-first search — cp-algorithms](https://cp-algorithms.com/graph/depth-first-search.html)
- [Flood fill — Wikipedia](https://en.wikipedia.org/wiki/Flood_fill)
- [Iterative deepening depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
