---
id: graph-shortest-paths
title: Shortest paths with weights
level: intermediate
minutes: 15
summary: Dijkstra with a binary heap and why negative edges break it, Bellman–Ford and negative cycles, 0-1 BFS, and A* with admissible heuristics.
---

BFS finds the path with the fewest edges. Once edges carry weights (kilometres, milliseconds, pounds), the fewest edges is no longer the cheapest. A motorway detour of 3 roads can beat a single slow lane.

This lesson covers the single-source problem: the cheapest distance from one source s to every other vertex. Assume finite graphs, finite numeric weights and valid adjacency entries for every vertex. The Python heap examples require mutually orderable vertex labels to break distance ties. Arithmetic and expected dictionary access are treated as constant-time. Every algorithm here is built on one operation.

## Relaxation

Keep a tentative distance `dist[v]` for every vertex, starting at infinity (0 for the source). The following fragment belongs inside a traversal with distances and parents already initialised. To **relax** an edge u→v of weight w is to ask "is going via u better than what I have?":

```python
if dist[u] + w < dist[v]:
    dist[v] = dist[u] + w
    parent[v] = u
```

Distances only ever decrease, and never drop below the true shortest distance. The algorithms differ only in *which* edges they relax, and in what order.

## Dijkstra's algorithm

Intuition: grow a region of "settled" vertices outward from s, always settling the unsettled vertex with the smallest tentative distance next. It is BFS where the queue is ordered by distance instead of arrival.

```python
import heapq
INF = float('inf')

def dijkstra(adj, s):
    dist = {s: 0}
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue  # stale entry
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist
```

Python's `heapq` has no "decrease key", so we push a new entry and skip outdated ones when they surface (**lazy deletion**). The heap holds O(m + 1) entries and can pop stale entries as well as live ones. For simple graphs, m ≤ n², giving the usual O((n + m) log(n + 1)) bound; arbitrary multigraphs need a log(m + 1) term for this lazy implementation.

### A worked trace

```
S --4--> A --1--> C --3--> T
 \      ^        ^
  1    2        5
   \  /        /
    B --------+
```

Edges: S→A 4, S→B 1, B→A 2, B→C 5, A→C 1, C→T 3.

The table lists nonstale pops; obsolete A(4) and C(6) entries are skipped.

| Pop | dist after relaxing |
|---|---|
| S (0) | A 4, B 1 |
| B (1) | A 3, C 6 |
| A (3) | C 4 |
| C (4) | T 7 |
| T (7) | done |

The direct edge S→A (4) loses to S→B→A (3), and C improves twice. Final: S 0, B 1, A 3, C 4, T 7.

### Why it is correct

When u is popped with the smallest tentative distance d, could a cheaper path to u exist? Any such path must leave the settled region somewhere, through some unsettled vertex x with `dist[x] ≥ d`. From x onward it can only add **non-negative** weight, so it costs at least d. So d is final.

### Complexity

| Priority queue | Time |
|---|---|
| Binary heap | O((n + m) log n) |
| Fibonacci heap | O(m + n log n) |
| Unsorted array | O(n²) |

For dense graphs, the O(n²) array bound avoids the binary-heap bound’s logarithmic factor. Fibonacci heaps improve the asymptotic decrease-key bound. Actual speed depends on implementation, successful relaxations and workload; these bounds do not establish a universal winner.

### Why negative edges break it

The correctness argument assumed that extending a path never makes it cheaper. A negative edge breaks exactly that.

```
A --4--> B --2--> D
 \      ^
  5   -3
   \  /
    C
```

1. Pop A: B = 4, C = 5.
2. Pop B (4) and settle it: D = 6.
3. Pop C (5): C→B gives 5 − 3 = 2, better than 4. But B is already settled and its edge to D has already been used.

Textbook Dijkstra reports D = 6; the true answer is A→C→B→D = 4.

> [!warning] "My lazy version handled it"
> The lazy-deletion code above *does* re-push B with distance 2 and fixes D, because it never marks vertices as final. That variant gives correct answers with negative edges (but no negative cycles), but a vertex can be re-processed many times, and the worst case becomes exponential. Use Bellman–Ford instead.

You cannot fix negative edges by adding a constant to every weight either: a path with more edges gets penalised more, which changes which path is shortest.

## Bellman–Ford

Relax **every edge**, n − 1 times.

```python
def bellman_ford(n, edges, s):
    INF = float('inf')
    dist = [INF] * n
    dist[s] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break  # converged early
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None  # negative cycle
    return dist
```

Why n − 1 rounds? A shortest path without cycles has at most n − 1 edges. After round k, every shortest path that uses at most k edges is correct, because each round extends correct paths by one more edge.

On the negative-edge example above, Bellman–Ford correctly returns A 0, B 2, C 5, D 4.

If an n-th round can still improve something, a **negative cycle** is reachable from the source. Distances are unbounded below for vertices reachable from that cycle; other vertices can still have finite distances. This implementation returns None for the entire result when it detects one. Bellman–Ford detects this; Dijkstra cannot.

- **Time:** O(n + nm), including initialisation; conventionally O(nm) when m ≥ 1. For n = 10⁵ and m = 10⁶, the product nm is 10¹¹ edge-relaxation opportunities, not an elapsed-time prediction.
- **Real uses:** distance-vector routing protocols such as RIP are a distributed Bellman–Ford, each router relaxing the routes its neighbours advertise. Currency arbitrage detection takes w = −log(rate), so a cycle whose rates multiply to more than 1 becomes a negative cycle.

> [!note] SPFA
> The "Shortest Path Faster Algorithm" only re-relaxes edges out of vertices whose distance just changed, using a queue. Its performance depends on edge order and graph structure; its worst-case bound remains O(nm) when m ≥ 1.

## 0-1 BFS

If every weight is **0 or 1**, you do not need a heap. Use a **deque**: push to the front for a 0-edge (same distance) and to the back for a 1-edge (one more).

```python
from collections import deque

def zero_one_bfs(adj, s):
    dist = {s: 0}
    dq = deque([(0, s)])
    while dq:
        d, u = dq.popleft()
        if d != dist[u]:
            continue  # stale entry
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                if w == 0:
                    dq.appendleft((nd, v))
                else:
                    dq.append((nd, v))
    return dist
```

Queued distance labels occupy at most two consecutive values in nondecreasing order; obsolete entries are skipped. Thus, it behaves like Dijkstra's heap at O(1) per operation: **O(n + m)** total.

Typical problems: the fewest walls to break in a maze (stepping into a wall costs 1, open floor 0), or a grid where following the printed arrow is free and changing direction costs 1.

## A* search

Dijkstra settles vertices by distance from the source; obstacles, weights and connectivity shape the explored region. If you want one specific target and can **estimate** how far you are from it, you can steer the search.

A* orders the heap by **f(v) = g(v) + h(v)**:

- g(v) is the known cost from the start (Dijkstra's dist).
- h(v) is a heuristic estimate of the remaining cost to the goal.

```python
def astar(grid, start, goal):
    if not grid or not grid[0]:
        return None
    R, C = len(grid), len(grid[0])
    if any(len(row) != C for row in grid):
        raise ValueError("ragged grid")

    def h(p):  # Manhattan distance
        return (abs(p[0] - goal[0])
                + abs(p[1] - goal[1]))

    def ok(r, c):
        return (0 <= r < R and 0 <= c < C
                and grid[r][c] != '#')

    if not ok(*start) or not ok(*goal):
        return None
    g = {start: 0}
    pq = [(h(start), start)]
    while pq:
        f, u = heapq.heappop(pq)
        if u == goal:
            return g[u]
        if f > g[u] + h(u):
            continue  # stale
        r, c = u
        for v in ((r + 1, c), (r - 1, c),
                  (r, c + 1), (r, c - 1)):
            if not ok(*v):
                continue
            ng = g[u] + 1
            if ng < g.get(v, INF):
                g[v] = ng
                f = ng + h(v)
                heapq.heappush(pq, (f, v))
    return None
```

### Heuristic quality

For finite graphs with non-negative edge costs, h(goal) = 0 and a reachable goal:

- **Admissible**: h never overestimates the true remaining cost. A* that reopens a vertex when a better g is found and stops when the goal is popped returns an optimal path. Merely discovering the goal is not a safe stopping condition.
- **Consistent** (monotone): h(u) ≤ w(u, v) + h(v) for every edge. With h(goal) = 0 this implies admissibility, and no settled vertex needs reopening.
- **h = 0** gives Dijkstra’s ordering. **h = true distance** can still expand many vertices lying on different optimal paths; ties matter.

| Movement | Admissible h |
|---|---|
| 4-way grid, cost 1 | Manhattan |
| 8-way grid, straight cost 1 and diagonal √2 | Octile |
| 8-way grid, all moves cost 1 | Chebyshev |
| Geometric edges costing at least their Euclidean length | Euclidean |
| Travel time with a valid global speed upper bound | Straight-line distance ÷ that speed |

> [!tip] Trading optimality for speed
> **Weighted A*** uses f = g + ε·h with ε > 1. On a finite graph with non-negative costs, an admissible h with h(goal) = 0, reopening on improved g, and stopping when the goal is popped, the returned cost is at most ε times optimum. It can reduce expansions, but a speedup is not guaranteed.

Route-planning methods include contraction hierarchies and landmark heuristics (ALT).

> [!note] Content gap
> Product-specific implementations and millisecond/vertex-count performance claims are omitted: no identified dataset, implementation and reproducible measurement support them here.

## Choosing an algorithm

| Graph | Use | Time |
|---|---|---|
| Unweighted | BFS | O(n + m) |
| Weights 0/1 | 0-1 BFS | O(n + m) |
| Non-negative | Dijkstra, simple graph | O((n + m) log(n + 1)) |
| One target + h | A* | Depends on heuristic, ties and reopening |
| Negative edges | Bellman–Ford | O(n + nm) |
| DAG, any weights | Topo order | O(n + m) |

The last row: in a DAG, relax edges in topological order and each vertex is final when you reach it, even with negative weights.

## Key takeaways
- Every algorithm relaxes edges; they differ in which edges and in what order.
- Dijkstra settles the closest unsettled vertex each step; with a binary heap it is O((n + m) log n), and it is correct only for non-negative weights.
- Bellman–Ford takes O(n + nm), handles negative edges and detects negative cycles reachable from its source.
- 0-1 BFS uses a deque for weights in {0, 1} and runs in O(n + m).
- A* uses a heuristic: under the stated goal and reopening conditions admissibility preserves optimality; consistency avoids reopening; h = 0 gives Dijkstra’s ordering.

## Further reading
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Dijkstra — cp-algorithms](https://cp-algorithms.com/graph/dijkstra.html)
- [Bellman–Ford algorithm — Wikipedia](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm)
- [0-1 BFS — cp-algorithms](https://cp-algorithms.com/graph/01_bfs.html)
- [Introduction to A* — Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
