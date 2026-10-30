---
id: graph-low-link-failures
title: Bridges and articulation points from low links
level: advanced
minutes: 4
sourceLesson: graph-advanced
summary: Strict versus non-strict low-link comparisons answer different failure questions.
---

DFS discovery order was covered earlier. This low-link calculation is for a simple undirected graph; Tarjan’s SCC low links earlier served a different directed-graph purpose. Here n counts vertices and m counts edges.

## Bridges and articulation points

In an undirected network:

- A **bridge** is an edge whose removal increases the number of connected components.
- An **articulation point** (cut vertex) is a vertex whose removal, with its incident edges, increases that number.

These are single points of failure: the one fibre link between two regions, the one router everything passes through.

> [!analogy] Real-world analogy: a housing estate with one way in
> A housing estate joined to the town by a single road is cut off if that road is closed. A roundabout that every route between two districts must pass through cuts them apart if it is shut, even though no single road is the problem.
>
> **How it maps:** the lone access road is a bridge, an edge on no cycle. The unavoidable roundabout is an articulation point, a vertex whose removal disconnects the graph. Roads around a ring, with a detour available, are neither.
>
> **Where it stops:** a closed road in real life slows traffic down without always cutting anyone off completely, because people walk or take other modes. In the graph, removal is all or nothing, and the question is purely whether any path survives.

### Low-link values

Run DFS and record `tin[u]`, the time u was discovered. Define `low[u]` as the smallest `tin` reachable from u's subtree using tree edges downwards plus **at most one** back edge.

In symbols:

```formula reference
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
In words: a vertex's low value is the earliest discovery time its DFS subtree can reach with at most one back edge. If a child's subtree cannot climb back to its parent or above, the edge to that child is a bridge; if it cannot climb above the parent, the parent is a single point of failure (unless it is the root).
```

For the example below, with adjacency lists in increasing order, DFS from 0 visits 0, 1, 2, 3, 4, 5, 6 in that order. Vertex 3 has discovery and low-link values of three, while vertex 1 has discovery value one. The strict bridge test therefore identifies 1–3.

For a tree edge u→v (v a child of u):

- If `low[v] > tin[u]`, nothing in v's subtree can get back to u or above without using u–v. So **u–v is a bridge**.
- If `low[v] >= tin[u]` and u is not the root, v's subtree cannot get above u without passing through u. So **u is an articulation point**.
- The **tree root** is an articulation point if and only if it has **two or more DFS children**.

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
            # Skip the same undirected
            # parent edge.
            if v == p:
                continue
            if tin[v] != -1:  # back edge
                low[u] = min(low[u], tin[v])
                continue
            dfs(v, u)
            children += 1
            # Propagate the child subtree’s
            # escape.
            low[u] = min(low[u], low[v])
            if low[v] > tin[u]:
                # No route bypasses this
                # parent edge.
                bridges.append((u, v))
            if p != -1 and low[v] >= tin[u]:
                # Removing u separates a
                # child subtree.
                cuts.add(u)
        if p == -1 and children > 1:
            # Removing u separates a child
            # subtree.
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
- Strict versus non-strict low-link comparisons answer different failure questions.
- The DFS root needs its own articulation-point test.
- Parallel-edge inputs need parent edge identities.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Bridge (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Bridge_(graph_theory))
- [Finding articulation points — cp-algorithms](https://cp-algorithms.com/graph/cutpoints.html)
- [Finding bridges — cp-algorithms](https://cp-algorithms.com/graph/bridge-searching.html)
