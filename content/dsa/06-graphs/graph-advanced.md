---
id: graph-advanced
title: Flow, matching, bridges and articulation points
level: advanced
minutes: 16
summary: Maximum flow with Ford–Fulkerson and Edmonds–Karp, the max-flow min-cut theorem, bipartite matching as flow, and finding single points of failure with DFS low-link values.
---

This lesson covers three ideas that turn up in real systems and senior interviews: how much can a network carry (**max flow**), how to pair things up optimally (**matching**), and which single link or node would break a network if it failed (**bridges and articulation points**).

## Network flow

### The model

A **flow network** is a directed graph where each edge has an **edge capacity**: the most it can carry, in litres per second, Gbit/s, lorries per day. There is a **source** s where everything starts and a distinct **sink** t where it ends. Assume finite capacities. A **flow** assigns an amount to each edge, obeying two rules:

```formula
0 ≤ f(u, v) ≤ c(u, v)
Σ_x f(x, v) = Σ_y f(v, y)   for v ≠ s, t
|f| = Σ_y f(s, y) − Σ_x f(x, s)
where
u, v: the start and end of an edge u→v
x: any vertex with an edge into v (or into s)
y: any vertex with an edge out of v (or out of s)
s: the source vertex
t: the sink vertex
c(u, v): the edge capacity of u→v, never negative
f(u, v): the flow sent along edge u→v
Σ_x, Σ_y: add up over every such vertex x or y
≠: is not equal to
|f|: the value of the flow: the net amount leaving s
≤: is at most
In words: each edge carries between nothing and its edge capacity (the **capacity constraint**); every vertex except s and t passes on exactly what it receives (**flow conservation** rule); and the flow's value is what leaves the source.
```

For example, a pipe with an edge capacity of 10 litres per second can carry 0 to 10, and a junction receiving 7 must send out 7. The **maximum flow** problem asks for the largest possible value.

```
s --10--> a ---4----> t
|         | \        ^
10        2  8       |
|         |   \      | 10
|         v     v    |
+---10--> b -9-> c --+
```

Edges: s→a 10, s→b 10, a→b 2, a→t 4, a→c 8, b→c 9, c→t 10. The maximum flow is **14**.

### Why greedy fails

The obvious approach: find any s→t path with unused edge capacity, push as much as you can, repeat. It can get stuck.

```
     s
    / \
   1   1
  v     v
  a -1-> b
  |      |
  1      1
  v      v
  t <----+
```

Edges s→a, s→b, a→b, a→t, b→t, each with edge capacity 1. If greedy first picks s→a→b→t, it uses up s→a and b→t. Now s→b leads only to b, whose exit is full. Greedy stops at 1, but the max is 2 (s→a→t and s→b→t).

### The residual graph

The fix is to allow **undoing** flow. For each edge, the residual graph records how much more you could push forwards and how much you could cancel:

```formula
r(u, v) = c(u, v) − f(u, v)
r(v, u) = f(u, v)
r(u, v) = 10 − 6 = 4,  r(v, u) = 6
where
u, v: the ends of an original edge u→v
c(u, v): its edge capacity; 10 in the example
f(u, v): the flow it currently carries; 6 in the example
r(u, v): the **forward residual**: unused edge capacity on u→v
r(v, u): the **backward residual**: how much of the u→v flow you may cancel by "sending" along v→u
In words: you can push up to the unused edge capacity forwards, and you can push up to the current flow backwards, which undoes it.
```

So:

- the **forward residual** u→v is the unused edge capacity;
- this edge contributes a **backward residual** on v→u equal to its flow, meaning “you may cancel up to that many units”. With an original antiparallel edge, aggregate residual capacity also includes that opposite edge’s unused edge capacity.

An **augmenting path** is any s→t path in this residual graph. In the example, after the bad first path, the residual has s→b (1), the backward edge b→a (1), and a→t (1). Pushing along s→b→a→t cancels the a→b flow and reroutes it, giving 2.

### Ford–Fulkerson and Edmonds–Karp

**Ford–Fulkerson** is the method: while an augmenting path exists, push its bottleneck capacity along it.

- With integer capacities each augmentation adds at least 1, so the number of augmentations is at most the answer itself:

```formula
A ≤ |f*|
T = O(m × |f*|)
A = 2 × 10^6
where
A: the number of augmentations
|f*|: the value of the maximum flow; 2 × 10^6 in the bad case
m: the number of edges; each augmentation's search costs O(m)
T: Ford–Fulkerson's running time with integer capacities
O(…): Big O: grows at most this fast, up to a constant factor
≤: is at most
In words: each path adds at least one unit, so you may need as many searches as the size of the answer.
```

  That can be awful if capacities are large: in the classic bad case, paths alternate back and forth across a middle edge with edge capacity 1, needing two million augmentations when the other capacities are a million.
- With irrational capacities a bad path choice may never terminate.

**Edmonds–Karp** fixes the choice: always use the **shortest** augmenting path (fewest edges), found by BFS. That bounds the number of augmentations, whatever the capacities:

```formula
A = O(n × m)
T = O(n × m) × O(m) = O(n × m^2)
n × m^2 = 10^3 × (10^4)^2 = 10^11
where
n: the number of vertices; 1,000 in the example
m: the number of edges; 10,000 in the example
A: the number of augmenting paths Edmonds–Karp uses
T: the total running time (each BFS costs O(m))
O(…): Big O: grows at most this fast, up to a constant factor
In words: at most about n × m shortest paths, each found by a BFS over m edges.
```

So the total is **O(n m²)**, in the unit-cost arithmetic model, independent of how large the edge capacities are. The 10¹¹ figure is a worst-case growth expression; real runs usually need far fewer augmentations. Integer bit lengths and floating-point error require separate consideration.

```python
from collections import deque, defaultdict

def max_flow(cap, s, t):
    # Exact integer capacities.
    if s == t:
        raise ValueError("same terminals")
    res = defaultdict(dict)
    for u in cap:
        for v, c in cap[u].items():
            if type(c) is not int or c < 0:
                raise ValueError("capacity")
            res[u][v] = res[u].get(v, 0) + c
            # reverse edge, initially 0
            res[v].setdefault(u, 0)
    flow = 0
    while True:
        par = {s: None}
        q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v, c in res[u].items():
                if c > 0 and v not in par:
                    par[v] = u
                    q.append(v)
        if t not in par:
            return flow, res
        b, v = float('inf'), t
        while par[v] is not None:
            b = min(b, res[par[v]][v])
            v = par[v]
        v = t
        while par[v] is not None:
            u = par[v]
            res[u][v] -= b
            res[v][u] += b
            v = u
        flow += b
```

On the first example it returns `(14, residual_graph)`: the flow value and the final residual capacities.

> [!note] Faster algorithms
> **Dinic's algorithm** pushes many shortest paths at once using BFS levels and DFS blocking flows: O(n²m) in general and O(m√n) (√ is the square root; n vertices, m edges) on unit networks such as the standard bipartite matching reduction. Arbitrary unit-capacity networks need a different bound; edge capacity 1 alone does not establish O(m√n). Push-relabel is another family whose performance depends on the instance and implementation.

A useful fact: with integer capacities there is always an **integer** maximum flow, and these algorithms find one. This is what makes flow usable for counting and assignment problems.

## Max-flow min-cut

An **s–t cut** splits the vertices into S (containing s) and T (containing t). Its **cut capacity** is the total edge capacity of edges going **from S to T** (edges from T back to S do not count):

```formula
c(S, T) = Σ c(u, v)   for u in S, v in T
c(S, T) = c(a, t) + c(c, t) = 4 + 10 = 14
|f| ≤ c(S, T)
where
S: the set of vertices on the source side, including s
T: the set on the sink side, including t
u, v: the ends of an edge u→v that goes from S to T
c(u, v): the edge capacity of u→v
c(S, T): the cut capacity
a, c, t: vertices of the first example (c here is a vertex name, not an edge capacity)
|f|: the value of any flow
Σ: add up over every such edge
≤: is at most
In words: the cut capacity is the total of its forward-crossing edges, and no flow can exceed it, because every unit must cross from S to T.
```

The worked line uses the cut S = {s, a, b, c}, T = {t} from the first example.

> [!note] Max-flow min-cut theorem
> The maximum flow value equals the minimum cut capacity over all s–t cuts.

The intuition: every unit of flow must cross every cut, so the flow value is at most any cut capacity (the last line above). When Ford–Fulkerson stops, let S be the vertices still reachable from s in the residual graph. Every edge S→T is a saturated edge, full to its edge capacity (or it would be in the residual), and every edge T→S carries 0 (or its backward residual would be usable). So the flow equals that cut capacity, and both are optimal.

In the first example, after the algorithm finishes, S = {s, a, b, c}, T = {t}. The cut edges are a→t (4) and c→t (10): cut capacity **14**, matching the flow. Increasing only links outside this cut cannot raise the maximum flow while its cut capacity stays 14. Other engineering objectives or coordinated upgrades can still justify those changes.

Uses of min cut:

- **Image segmentation**: pixels are vertices, the source means "foreground", the sink "background", and edge capacities penalise cutting between similar neighbours. The min cut optimises the specified representable segmentation energy (the basis of "graph cuts" in computer vision).
- **Network reliability**: the minimum number of links whose failure disconnects two data centres equals the max flow with unit capacities.
- **Baseball elimination** and **project selection** reduce neatly to min cut.

## Bipartite matching

A **matching** is a set of edges with no shared vertex. In a bipartite graph (workers and jobs, riders and drivers), a **maximum matching** pairs up as many as possible.

### As a flow problem

```
s   -> Ann, Bob, Cat   (cap 1)
Ann -> X, Y            (cap 1)
Bob -> X               (cap 1)
Cat -> Y, Z            (cap 1)
X, Y, Z -> t           (cap 1)
```

Add a source joined to every worker and a sink joined from every job, all capacities 1, and direct the worker→job edges. An integer max flow is a maximum matching: each worker sends at most 1 unit, each job receives at most 1.

### Kuhn's algorithm (augmenting paths)

The flow view specialises into a short DFS. For each left vertex u, try to find a right vertex v that is free, or whose current partner can be moved elsewhere.

```python
def kuhn(left, adj):
    match = {}  # right -> left

    def augment(u, seen):
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in match:
                match[v] = u
                return True
            if augment(match[v], seen):
                match[v] = u
                return True
        return False

    return sum(augment(u, set())
               for u in dict.fromkeys(left))
```

With Ann→{X, Y}, Bob→{X}, Cat→{Y, Z}: Ann takes X. Bob wants X, so Ann is asked to move, and moves to Y. Cat tries Y: Ann would have to move back to X, which would need Bob to move, and Bob has nowhere else to go. That fails, so Cat takes Z. Result: 3 pairs.

With n vertices and m edges in the bipartite graph:

```formula
T_K = O(n_L × m)
T_HK = O((n + m) × √n)
T_K ≈ 10^5 × 10^6 = 10^11
T_HK ≈ 1.2 × 10^6 × √(2 × 10^5)
T_HK ≈ 5.4 × 10^8
where
n: the number of vertices; 2 × 10^5 in the example
n_L: the number of left vertices; 10^5 in the example
m: the number of edges; 10^6 in the example
T_K: Kuhn's algorithm: one DFS of O(m) per left vertex
T_HK: Hopcroft–Karp: O(√n) phases of O(n + m) each
√: the square root
≈: approximately equal to
O(…): Big O: grows at most this fast, up to a constant factor
In words: Hopcroft–Karp needs only about √n rounds instead of one per vertex, which here is nearly two hundred times less work.
```

Kuhn's bound counts one search per left vertex; these are growth expressions, not measured times.

- Kuhn: O(n m).
- **Hopcroft–Karp**: finds many shortest augmenting paths per phase, O((n + m) √n), conventionally O(m √n) after isolated vertices are removed.
- **Weighted assignment** (minimise total cost while assigning every item on the required side, e.g. driver ETA, the estimated time of arrival): the **Hungarian algorithm**, O(n³) for an n × n assignment, or min-cost flow. Without a required cardinality, an empty matching can minimise non-negative cost.

> [!tip] König's theorem
> In a bipartite graph, the size of a maximum matching equals the size of a minimum **vertex cover** (the fewest vertices touching every edge). So max matching also answers "fewest guards to watch every corridor" when the graph is bipartite. In general graphs, minimum vertex cover is NP-hard.

## Bridges and articulation points

In an undirected network:

- A **bridge** is an edge whose removal increases the number of connected components.
- An **articulation point** (cut vertex) is a vertex whose removal, with its incident edges, increases that number.

These are single points of failure: the one fibre link between two regions, the one router everything passes through.

### Low-link values

Run DFS and record `tin[u]`, the time u was discovered. Define `low[u]` as the smallest `tin` reachable from u's subtree using tree edges downwards plus **at most one** back edge.

In symbols:

```formula
low(u) = min(tin(u), tin(b), low(v))
low(v) > tin(u)
low(v) ≥ tin(u)
where
u: a vertex; v: one of its children in the DFS tree
tin(u): u's discovery time: 0 for the first vertex DFS reaches, 1 for the next, and so on
b: any vertex u has a back edge to (an already-discovered vertex other than its parent)
low(v): the earliest discovery time v's subtree can reach with at most one back edge
min(…): the smallest of all these values, over every child v and every back edge
>: is greater than
≥: is at least
In words: the first line defines low. If the second line holds, v's subtree cannot climb back to u or above, so the edge u–v is its only link (a bridge). If the third line holds, the subtree cannot climb above u without passing through u, so u is a single point of failure (unless u is the root).
```

For the example below, with adjacency lists in increasing order, DFS from 0 visits 0, 1, 2, 3, 4, 5, 6 in that order: tin(3) = 3 and low(3) = 3, while tin(1) = 1, so low(3) > tin(1) and 1–3 is a bridge.

For a tree edge u→v (v a child of u):

- If `low[v] > tin[u]`, nothing in v's subtree can get back to u or above without using u–v. So **u–v is a bridge**.
- If `low[v] >= tin[u]` and u is not the root, v's subtree cannot get above u without passing through u. So **u is an articulation point**.
- The **root** is an articulation point if and only if it has **two or more DFS children**.

The implementation below assumes a simple undirected graph on vertices 0..n−1, with both directions present in adjacency lists.

```python
def bridges_and_cuts(n, adj):
    tin = [-1] * n
    low = [0] * n
    timer = 0
    bridges, cuts = [], set()

    def dfs(u, p):
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        children = 0
        for v in adj[u]:
            if v == p:
                continue
            if tin[v] != -1:  # back edge
                low[u] = min(low[u], tin[v])
                continue
            dfs(v, u)
            children += 1
            low[u] = min(low[u], low[v])
            if low[v] > tin[u]:
                bridges.append((u, v))
            if p != -1 and low[v] >= tin[u]:
                cuts.add(u)
        if p == -1 and children > 1:
            cuts.add(u)

    for u in range(n):
        if tin[u] == -1:
            dfs(u, -1)
    return bridges, cuts
```

```
  0         4
  | \      / |
  |  1 -- 3  |
  | /      \ |
  2         5 -- 6
```

Two triangles {0, 1, 2} and {3, 4, 5}, joined by 1–3, with 6 hanging off 5. The function returns bridges 5–6 and 1–3 and articulation points {1, 3, 5}. Edges inside a triangle are never bridges: each has a detour.

One DFS: **O(n + m)** for n vertices and m edges. As with undirected cycle detection, skip the parent by edge id rather than vertex if parallel edges are possible, because a doubled link is not a bridge.

> [!example] In practice
> Network engineers run exactly this on topology graphs to find links and routers that need redundancy. Removing all bridges splits a graph into **2-edge-connected components**; grouping edges around articulation points gives **biconnected components**, which are used in planarity testing and circuit analysis.

## Key takeaways
- Max flow pushes flow along augmenting paths in the residual graph; backward residual edges let later paths undo earlier choices.
- Edmonds–Karp picks shortest augmenting paths by BFS for an O(n m²) bound (n vertices, m edges); with integer capacities the max flow can be chosen integer-valued.
- Max-flow min-cut: the max flow equals the smallest total edge capacity from S to T, and the vertices reachable in the final residual graph give that cut.
- Bipartite matching is unit-capacity flow; Kuhn's algorithm is O(n m) and Hopcroft–Karp O(m √n).
- DFS low-link values find bridges (low[v] > tin[u]) and articulation points (low[v] ≥ tin[u], or a root with 2+ children) in O(n + m).

## Further reading
- [Maximum flow problem — Wikipedia](https://en.wikipedia.org/wiki/Maximum_flow_problem)
- [Edmonds–Karp — cp-algorithms](https://cp-algorithms.com/graph/edmonds_karp.html)
- [Max-flow min-cut theorem — Wikipedia](https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem)
- [Kuhn's algorithm for bipartite matching — cp-algorithms](https://cp-algorithms.com/graph/kuhn_maximum_bipartite_matching.html)
- [Hopcroft–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm)
- [Finding bridges — cp-algorithms](https://cp-algorithms.com/graph/bridge-searching.html)
- [Finding articulation points — cp-algorithms](https://cp-algorithms.com/graph/cutpoints.html)
