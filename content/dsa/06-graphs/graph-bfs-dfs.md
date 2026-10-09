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

Both traversals touch each vertex and each edge a bounded number of times, so their running time grows with the size of the graph:

```formula
T(n, m) = O(n + m)
where
T(n, m): the running time of one full BFS or DFS, counted in basic steps
n: the number of vertices (points) in the graph
m: the number of edges (connections) in the graph
O(…): Big O: grows at most this fast, up to a constant factor, once the graph is large
In words: the work is proportional to the number of vertices plus the number of edges, so doubling the graph roughly doubles the time.
```

For example, a road map with n = 1,000,000 junctions and m = 2,500,000 roads needs on the order of 3.5 million steps. This assumes adjacency lists and the usual constant-time access model; dictionary/set bounds here are expected bounds. All referenced vertices must have adjacency entries. What differs between BFS and DFS is the *order*, and that order is what makes each one useful. Throughout this lesson, n is the number of vertices and m the number of edges.

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

The key fact is an invariant (a rule that stays true at every step) about what the queue holds:

```formula
d = dist(v_front)
d ≤ dist(v_back) ≤ d + 1
where
dist(x): the number of edges from the source to vertex x, as BFS recorded it
x: any vertex
v_front: the vertex at the front of the queue (next to be dequeued)
v_back: the vertex at the back of the queue (most recently enqueued)
d: the distance of the front vertex, which is the layer BFS is currently finishing
≤: is at most
In words: the queue only ever holds vertices from two neighbouring layers, distance d at the front and d + 1 behind them, in that order.
```

In the trace above, after dequeuing 1 the queue is [2, 3, 4] with distances 1, 2, 2: never more than one apart. So BFS finishes every vertex at distance d before touching any at distance d + 1. The first time BFS reaches a vertex, it has reached it by the fewest possible edges. The invariant only holds because every edge counts as one step; with different edge costs it breaks.

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
> If you mark a vertex visited only when it is *dequeued*, it can be enqueued many times by different neighbours before it is processed. On a dense graph the queue can grow to O(m) entries (in proportion to m, the number of edges), and some versions compute wrong distances. Mark (or set `dist`) at the moment you enqueue.

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

This one visits 0, 2, 4, 5, 1, 3. It is still a valid DFS, but the order differs because the *last* neighbour pushed is popped first. Push neighbours in reverse if you need the recursive order. Note that here the `seen` check happens on pop, so a vertex may sit on the stack more than once; that is fine and still O(n + m) overall, where n is the number of vertices and m the number of edges.

## Complexity

With an adjacency list, BFS enqueues each vertex once, and both shown traversals scan each processed adjacency list once. The iterative DFS can push duplicates, but at most O(n + m) entries overall. Adding up the work per vertex gives the total:

```formula
W = n + Σ deg(u) = n + 2 × m
W = 6 + 2 × 6 = 18
O(n + m)
where
W: the total work of one traversal of an undirected graph, in basic steps
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
W = n × n = n^2
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

The frontier is the set of vertices discovered but not yet expanded. On a search tree where every node has the same number of children, the two traversals need very different amounts of frontier memory:

```formula
F_BFS ≈ b^d
F_DFS ≈ b × d
F_BFS ≈ 10^6 and F_DFS ≈ 60
where
F_BFS: the number of vertices BFS holds in its queue when it reaches depth d
F_DFS: the number of vertices DFS holds on its stack (the current path plus the waiting siblings at each level)
b: the branching factor: how many children each node has; 10 in the example
d: the depth: how many levels below the start the search reaches; 6 in the example
≈: approximately equal to
In words: BFS's frontier grows exponentially with depth, because a whole layer sits in the queue, while DFS's grows only in proportion to depth.
```

With b = 10 and d = 6, BFS holds about a million vertices while DFS holds about 60. The estimate assumes a full tree with no repeated states; on graphs with a visited set both still need memory for the set itself. That is why huge game-tree searches use DFS, or **iterative deepening** (DFS with depth limits 1, 2, 3, ...), which finds a shallowest goal with linear-depth search memory on finitely branching trees, using appropriate depth-limit handling.

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

Total work is still O(n + m), with n vertices and m edges: each vertex and edge is handled once across all traversals. (In a directed graph this gives "reachability trees", not strongly connected components; see lesson 3.)

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

Running BFS from every source separately multiplies the work by the number of sources:

```formula
W_separate = k × O(n + m)
W_multi = O(n + m)
where
W_separate: the work of k separate BFS runs, one per source
W_multi: the work of a single multi-source BFS
k: the number of sources (exits, hospitals, rotten oranges)
n: the number of vertices
m: the number of edges
O(…): Big O: grows at most this fast, up to a constant factor
In words: k separate searches cost k times as much as one, but a single search started from all sources at once costs the same as one ordinary BFS.
```

With 500 hospitals on a road graph, that is the difference between 500 traversals and one. So **put all sources in the queue at distance 0** and run one BFS.

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

So the state becomes `(row, col, keys)`, where `keys` is a bitmask: one bit per key, set to 1 if you hold it. The number of possible states is the number of cells times the number of key sets:

```formula
S = R × C × 2^K
S = 50 × 50 × 2^6
S = 2500 × 64 = 160000
where
S: the maximum number of distinct states (vertices of the state graph)
R: the number of grid rows; 50 here
C: the number of grid columns; 50 here
K: the number of different keys; 6 here
2^K: the number of possible sets of keys held, since each key is either held or not
In words: every cell can be visited once per combination of keys, so adding a key doubles the number of states.
```

So a 50 × 50 grid with 6 keys has at most 160,000 cell/key-set states; walls and reachability may reduce this. With 20 keys it would be over 2.6 billion, so this trick only suits a handful of keys. Assess memory for the chosen implementation. The same trick handles "you may break at most k walls" (state includes walls broken so far) or "move with remaining fuel f".

## Where these show up

- **Mark-and-sweep garbage collectors** mark live objects by traversing the reference graph from the roots (a multi-source traversal), then sweep whatever was not reached.
- **Web crawlers** traverse link graphs; their scheduling may use breadth-first ideas, priorities and per-site limits.
- **Degrees of separation** can be found with BFS. **Bidirectional BFS** searches from both ends; in directed graphs the backward search follows reversed edges. In a roughly tree-like model, two half-depth searches are much smaller than one full-depth search:

```formula
F_one ≈ b^d
F_two ≈ 2 × b^{d/2}
F_one ≈ 100^6 = 10^12
F_two ≈ 2 × 100^3 = 2 × 10^6
where
F_one: frontier vertices for one search from the start to depth d
F_two: frontier vertices for two searches, each going to depth d/2
b: the branching factor (average neighbours per vertex), greater than 1; 100 in the example
d: the length of the shortest path between the two people, in edges; 6 in the example
≈: approximately equal to
In words: meeting in the middle replaces one huge exponential with two much smaller ones, because b^d is b^{d/2} squared.
```

With 100 contacts each and six degrees of separation, that is about two million vertices instead of a trillion. Overlap between friend lists, degree variation and stopping rules affect actual work.

> [!note] Content gap
> No claim is made about LinkedIn’s current implementation: an authoritative implementation description was not verified.
- **Build tools and package managers** use DFS to walk dependency trees.

## Pitfalls

- **Forgetting the visited set** on a graph with cycles: the traversal loops forever.
- **Using DFS for "fewest steps".** DFS finds *a* path, not the shortest.
- **`list.pop(0)` as a queue** is O(n) per pop in Python, where n is the current queue length, because every remaining item moves one place left. Use `collections.deque`.
- **Missing disconnected parts.** A single traversal only covers one component.

## Key takeaways
- BFS uses a queue and explores in layers; in an unweighted graph the first visit to a vertex is via a shortest path.
- DFS uses a stack (or recursion) and goes deep first; it is the basis for cycle detection and ordering.
- Both are O(n + m) with an adjacency list (O(n²) with a matrix), for n vertices and m edges, and need a visited set to avoid loops.
- Mark vertices visited when you enqueue them, not when you dequeue them.
- Components and flood fill are "traverse from every unvisited vertex"; multi-source BFS starts with every source in the queue.

## Further reading
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-first search — cp-algorithms](https://cp-algorithms.com/graph/breadth-first-search.html)
- [Depth-first search — cp-algorithms](https://cp-algorithms.com/graph/depth-first-search.html)
- [Flood fill — Wikipedia](https://en.wikipedia.org/wiki/Flood_fill)
- [Iterative deepening depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
