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

A **flow network** is a directed graph where each edge u→v has a **capacity** c(u, v) ≥ 0: litres per second, Gbit/s, lorries per day. There is a **source** s and a distinct **sink** t. Assume finite capacities. A **flow** assigns f(u, v) to each edge such that:

1. **Capacity**: 0 ≤ f(u, v) ≤ c(u, v).
2. **Conservation**: at every vertex except s and t, flow in equals flow out.

The **value** of the flow is the net amount leaving s. The **maximum flow** problem asks for the largest possible value.

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

The obvious approach: find any s→t path with spare capacity, push as much as you can, repeat. It can get stuck.

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

Edges s→a, s→b, a→b, a→t, b→t, each capacity 1. If greedy first picks s→a→b→t, it uses up s→a and b→t. Now s→b leads only to b, whose exit is full. Greedy stops at 1, but the max is 2 (s→a→t and s→b→t).

### The residual graph

The fix is to allow **undoing** flow. For an edge u→v carrying f units out of c:

- the **forward residual** u→v has c − f spare;
- this edge contributes **backward residual** capacity f on v→u, meaning “you may cancel up to f units”. With an original antiparallel edge, aggregate residual capacity also includes that opposite edge’s unused capacity.

An **augmenting path** is any s→t path in this residual graph. In the example, after the bad first path, the residual has s→b (1), the backward edge b→a (1), and a→t (1). Pushing along s→b→a→t cancels the a→b flow and reroutes it, giving 2.

### Ford–Fulkerson and Edmonds–Karp

**Ford–Fulkerson** is the method: while an augmenting path exists, push its bottleneck capacity along it.

- With integer capacities each augmentation adds at least 1, so it terminates in at most |f*| augmentations: O(m · |f*|). That can be awful if capacities are large (in the classic bad case, paths alternate back and forth across a capacity-1 middle edge, needing two million augmentations when the other capacities are a million).
- With irrational capacities a bad path choice may never terminate.

**Edmonds–Karp** fixes the choice: always use the **shortest** augmenting path (fewest edges), found by BFS. That bounds the number of augmentations by O(nm), so the total is **O(n m²)**, in the unit-cost arithmetic model, independent of capacity magnitudes. Integer bit lengths and floating-point error require separate consideration.

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
> **Dinic's algorithm** pushes many shortest paths at once using BFS levels and DFS blocking flows: O(n²m) in general and O(m√n) on unit networks such as the standard bipartite matching reduction. Arbitrary unit-capacity networks need a different bound; capacity 1 alone does not establish O(m√n). Push-relabel is another family whose performance depends on the instance and implementation.

A useful fact: with integer capacities there is always an **integer** maximum flow, and these algorithms find one. This is what makes flow usable for counting and assignment problems.

## Max-flow min-cut

An **s–t cut** splits the vertices into S (containing s) and T (containing t). Its **capacity** is the total capacity of edges going **from S to T** (edges from T back to S do not count).

> [!note] Max-flow min-cut theorem
> The maximum flow value equals the minimum capacity of any s–t cut.

The intuition: every unit of flow must cross every cut, so flow ≤ any cut. When Ford–Fulkerson stops, let S be the vertices still reachable from s in the residual graph. Every edge S→T is saturated (or it would be in the residual), and every edge T→S carries 0 (or its backward residual would be usable). So the flow equals that cut's capacity, and both are optimal.

In the first example, after the algorithm finishes, S = {s, a, b, c}, T = {t}. The cut edges are a→t (4) and c→t (10): capacity **14**, matching the flow. Increasing only links outside this cut cannot raise the maximum flow while its capacity stays 14. Other engineering objectives or coordinated upgrades can still justify those changes.

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

- Kuhn: O(n m).
- **Hopcroft–Karp**: finds many shortest augmenting paths per phase, O((n + m) √n), conventionally O(m √n) after isolated vertices are removed.
- **Weighted assignment** (minimise total cost while assigning every item on the required side, e.g. driver ETA): the **Hungarian algorithm**, O(n³) for an n × n assignment, or min-cost flow. Without a required cardinality, an empty matching can minimise non-negative cost.

> [!tip] König's theorem
> In a bipartite graph, the size of a maximum matching equals the size of a minimum **vertex cover** (the fewest vertices touching every edge). So max matching also answers "fewest guards to watch every corridor" when the graph is bipartite. In general graphs, minimum vertex cover is NP-hard.

## Bridges and articulation points

In an undirected network:

- A **bridge** is an edge whose removal increases the number of connected components.
- An **articulation point** (cut vertex) is a vertex whose removal, with its incident edges, increases that number.

These are single points of failure: the one fibre link between two regions, the one router everything passes through.

### Low-link values

Run DFS and record `tin[u]`, the time u was discovered. Define `low[u]` as the smallest `tin` reachable from u's subtree using tree edges downwards plus **at most one** back edge.

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

One DFS: **O(n + m)**. As with undirected cycle detection, skip the parent by edge id rather than vertex if parallel edges are possible, because a doubled link is not a bridge.

> [!example] In practice
> Network engineers run exactly this on topology graphs to find links and routers that need redundancy. Removing all bridges splits a graph into **2-edge-connected components**; grouping edges around articulation points gives **biconnected components**, which are used in planarity testing and circuit analysis.

## Key takeaways
- Max flow pushes flow along augmenting paths in the residual graph; backward residual edges let later paths undo earlier choices.
- Edmonds–Karp picks shortest augmenting paths by BFS for an O(n m²) bound; with integer capacities the max flow is integral.
- Max-flow min-cut: the max flow equals the smallest total capacity of edges from S to T, and the vertices reachable in the final residual graph give that cut.
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
