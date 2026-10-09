---
id: graph-shortest-paths
title: Shortest paths with weights
level: intermediate
minutes: 15
summary: Dijkstra with a binary heap and why negative edges break it, Bellman–Ford and negative cycles, 0-1 BFS, and A* with admissible heuristics.
---

BFS finds the path with the fewest edges. Once edges carry weights (kilometres, milliseconds, pounds), the fewest edges is no longer the cheapest. A motorway detour of 3 roads can beat a single slow lane.

This lesson covers the single-source problem: the cheapest distance from one source s to every other vertex. Assume finite graphs, finite numeric weights and valid adjacency entries for every vertex. The Python heap examples require mutually orderable vertex labels to break distance ties. Arithmetic and expected dictionary access are treated as constant-time. Throughout, n is the number of vertices, m the number of edges, w(u, v) the weight of the edge from u to v, and O(…) is Big O notation: how the running time grows with n and m, ignoring constant factors. Every algorithm here is built on one operation.

## Relaxation

Keep a tentative distance `dist[v]` for every vertex, starting at infinity (0 for the source). The following fragment belongs inside a traversal with distances and parents already initialised. To **relax** an edge u→v of weight w is to ask "is going via u better than what I have?":

```formula
dist(v) ← min(dist(v), dist(u) + w)
dist(v) ← min(9, 3 + 4) = 7
where
u: the vertex the edge leaves
v: the vertex the edge enters
w: the weight of the edge u→v (a distance, time or cost)
dist(v): the best distance from the source s to v found so far; starts at ∞ for every vertex except s, which starts at 0
∞: infinity: "no path found yet"
min(…): the smaller of the two values
←: replace the value on the left with the value on the right
In words: if reaching u and then taking the edge is cheaper than the best route to v so far, remember that cheaper route.
```

In the worked line, v's best so far is 9, u is 3 away and the edge costs 4, so v improves to 7. In Python:

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

Python's `heapq` has no "decrease key", so we push a new entry and skip outdated ones when they surface (**lazy deletion**). The heap holds O(m + 1) entries and can pop stale entries as well as live ones. Each push or pop costs time proportional to the logarithm of the heap size, and in a simple graph the heap size cannot outgrow n² by much:

```formula
m ≤ n^2
log(m + 1) ≤ log(n^2 + 1) ≈ 2 × log(n)
T = O((n + m) × log(n + 1))
where
n: the number of vertices
m: the number of edges
log: the logarithm (base 2 here): how many times you can halve a number before reaching 1
T: the running time of lazy-deletion Dijkstra
≤: is at most
≈: approximately equal to
O(…): Big O: grows at most this fast, up to a constant factor
In words: a heap of up to m entries costs log m per operation, and because m is at most n² that is at most about twice log n, which Big O ignores.
```

For a simple graph with n = 1,000 vertices, the heap's log factor is at most about log₂(10⁶) ≈ 20 rather than log₂(1,000) ≈ 10: a constant factor, so the bound is unchanged. Arbitrary multigraphs (with repeated edges) can have m far above n², so they need a log(m + 1) term for this lazy implementation.

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

When u is popped with the smallest tentative distance d, could a cheaper path to u exist? Any such path P must leave the settled region somewhere, through some unsettled vertex x:

```formula
cost(P) ≥ dist(x) ≥ d
where
P: any path from the source to u
x: the first vertex on P outside the settled region
cost(P): the total weight of P
dist(x): x's tentative distance, which is at most the cost of P's part up to x
d: the tentative distance with which u was popped, the smallest of all unsettled vertices
≥: is at least
In words: the rest of P after x adds only non-negative weight, and x itself is no closer than u, so P cannot beat d.
```

So d is final. The first inequality is exactly where non-negative weights are needed: a negative edge after x could make P cheaper than dist(x).

### Complexity

Here n is the number of vertices and m the number of edges. With a binary heap, every vertex is popped and every edge may push, each costing a logarithmic heap operation:

```formula
T = O((n + m) × log(n))
(n + m) × log_2(n) ≈ 5 × 10^6 × 20 = 10^8
where
T: the running time of Dijkstra with a binary heap
n: the number of vertices; 10^6 in the example
m: the number of edges; 4 × 10^6 in the example
log(n): the logarithm of n; log_2(10^6) ≈ 20
log_2: the base-2 logarithm
≈: approximately equal to
O(…): Big O: grows at most this fast, up to a constant factor
In words: each of the n + m heap operations costs about log n steps.
```

A road graph of a million junctions and four million road segments needs on the order of 10⁸ basic steps; that is a scale estimate, not a measured time.

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

Why n − 1 rounds? A shortest path without cycles visits each vertex at most once, so it has at most one edge fewer than there are vertices:

```formula
k_max = n − 1
k_max = 4 − 1 = 3
where
n: the number of vertices; 4 in the example (A, B, C, D)
k_max: the most edges a cycle-free path can have, and so the number of rounds needed
In words: after round k, every shortest path using at most k edges is correct, and no shortest path needs more than n − 1 edges.
```

Each round extends correct paths by one more edge, so after round 3 on the four-vertex example every distance is final.

On the negative-edge example above, Bellman–Ford correctly returns A 0, B 2, C 5, D 4.

If an n-th round can still improve something, a **negative cycle** is reachable from the source. Distances are unbounded below for vertices reachable from that cycle; other vertices can still have finite distances. This implementation returns None for the entire result when it detects one. Bellman–Ford detects this; Dijkstra cannot.

- **Time:** up to n − 1 rounds, each relaxing all m edges:

```formula
T = O(n + n × m)
n × m = 10^5 × 10^6 = 10^11
where
T: Bellman–Ford's running time, including setting up the n distances
n: the number of vertices; 10^5 in the example
m: the number of edges; 10^6 in the example
O(…): Big O: grows at most this fast, up to a constant factor
In words: every round looks at every edge, so the work is the number of vertices times the number of edges.
```

  It is conventionally written O(nm) when m ≥ 1. The 10¹¹ figure counts edge-relaxation opportunities; it is not an elapsed-time prediction.
- **Real uses:** distance-vector routing protocols such as RIP are a distributed Bellman–Ford, each router relaxing the routes its neighbours advertise. Currency arbitrage detection turns exchange rates into weights with a logarithm, which turns multiplying rates into adding weights:

```formula
w = −log(r)
r_1 × r_2 × r_3 > 1
w_1 + w_2 + w_3 < 0
where
r: an exchange rate, units of the target currency per unit of the source
w: the edge weight given to that exchange
r_1, r_2, r_3: the rates on the three exchanges of a round trip
w_1, w_2, w_3: their weights
log: the logarithm (any fixed base); log of a number above 1 is positive, below 1 negative
In words: a round trip that ends with more money than it started with has weights summing below zero, a negative cycle.
```

  For example, rates 0.9, 0.9 and 1.25 multiply to 1.0125, a 1.25% profit, so their weights sum to a negative number and Bellman–Ford flags the cycle.

> [!note] SPFA
> The "Shortest Path Faster Algorithm" only re-relaxes edges out of vertices whose distance just changed, using a queue. Its performance depends on edge order and graph structure; its worst-case bound remains O(nm) (vertices times edges) when m ≥ 1.

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

Queued distance labels occupy at most two consecutive values in nondecreasing order; obsolete entries are skipped. Thus, it behaves like Dijkstra's heap at O(1) per operation: **O(n + m)** total, for n vertices and m edges.

Typical problems: the fewest walls to break in a maze (stepping into a wall costs 1, open floor 0), or a grid where following the printed arrow is free and changing direction costs 1.

## A* search

Dijkstra settles vertices by distance from the source; obstacles, weights and connectivity shape the explored region. If you want one specific target and can **estimate** how far you are from it, you can steer the search.

A* orders the heap by a priority that adds a guess of the remaining distance to the distance already travelled:

```formula
f(v) = g(v) + h(v)
f(v) = 6 + 4 = 10
where
v: a vertex waiting in the heap
g(v): the known cost from the start to v (Dijkstra's dist); 6 in the example
h(v): the heuristic: an estimate of the remaining cost from v to the goal; 4 in the example
f(v): the estimated total cost of the best path through v; the heap pops the smallest
In words: A* expands the vertex that looks cheapest overall, counting both the distance already travelled and a guess at the distance still to go.
```

A vertex 6 steps from the start and estimated 4 from the goal has priority 10, so it is expanded before one at g = 3 with h = 9 (priority 12). On a grid the usual estimate is the Manhattan distance, the number of up/down/left/right steps ignoring walls:

```formula
h(p) = |r_p − r_goal| + |c_p − c_goal|
h(p) = |2 − 5| + |7 − 3| = 3 + 4 = 7
where
p: the current cell
r_p, c_p: p's row and column
r_goal, c_goal: the goal's row and column
|x|: the absolute value of x: x without its minus sign
h(p): the estimated remaining cost, in moves
In words: count the rows and the columns you still have to cross; walls can only make the real path longer.
```

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

For finite graphs with non-negative edge costs, h(goal) = 0 and a reachable goal, two properties of h matter:

```formula
h(v) ≤ h*(v)
h(u) ≤ w(u, v) + h(v)
where
h(v): the heuristic estimate of the remaining cost from v to the goal
h*(v): the true cheapest remaining cost from v to the goal
u, v: the two ends of an edge u→v
w(u, v): the weight of that edge
≤: is at most
In words: the first line (admissible) says the guess never overestimates; the second (consistent) says the guess never drops by more than the cost of the edge you just took.
```

For example, Manhattan distance on a 4-way grid with cost-1 moves is consistent: one move changes it by at most 1, the cost of the move.

- **Admissible**: h never overestimates the true remaining cost (the first line). A* that reopens a vertex when a better g is found and stops when the goal is popped returns an optimal path. Merely discovering the goal is not a safe stopping condition.
- **Consistent heuristic** (monotone): the second line holds for every edge. With h(goal) = 0 this implies admissibility, and no settled vertex needs reopening.
- **h = 0** gives Dijkstra’s ordering. **h = true distance** can still expand many vertices lying on different optimal paths; ties matter.

| Movement | Admissible h |
|---|---|
| 4-way grid, cost 1 | Manhattan |
| 8-way grid, straight cost 1 and diagonal √2 ≈ 1.41 | Octile |
| 8-way grid, all moves cost 1 | Chebyshev |
| Geometric edges costing at least their Euclidean length | Euclidean |
| Travel time with a valid global speed upper bound | Straight-line distance ÷ that speed |

> [!tip] Trading optimality for speed
> **Weighted A* search** inflates the heuristic to search more greedily towards the goal. It can reduce expansions, but a speedup is not guaranteed. The price is a bounded loss of optimality, shown below.

On a finite graph with non-negative costs, an admissible h with h(goal) = 0, reopening on improved g, and stopping when the goal is popped, weighted A* returns a cost within a known factor of the best:

```formula
f(v) = g(v) + λ × h(v)
C ≤ λ × C*
C ≤ 1.5 × 100 = 150
where
v: a vertex in the heap
f(v): its priority; the heap pops the smallest
g(v): the known cost from the start to v
h(v): the heuristic estimate of the remaining cost to the goal
λ: the inflation weight, greater than 1; 1.5 in the example
C: the cost of the path weighted A* returns
C*: the cost of the true shortest path; 100 in the example
In words: weighting the heuristic by λ can make the answer at most λ times the optimum.
```

With λ = 1.5 and a true shortest cost of 100, the path found costs at most 150.

Route-planning methods include contraction hierarchies and landmark heuristics (ALT).

> [!note] Content gap
> Product-specific implementations and millisecond/vertex-count performance claims are omitted: no identified dataset, implementation and reproducible measurement support them here.

## Choosing an algorithm

In the table, n is the number of vertices, m the number of edges, h the A* heuristic, and log the logarithm.

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
- Dijkstra settles the closest unsettled vertex each step; with a binary heap it is O((n + m) log n) for n vertices and m edges, and it is correct only for non-negative weights.
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
