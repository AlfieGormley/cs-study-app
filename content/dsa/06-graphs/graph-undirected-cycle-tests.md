---
id: graph-undirected-cycle-tests
title: Undirected cycles and parent edges
level: intermediate
minutes: 2
sourceLesson: graph-dfs-applications
summary: Ignore the particular parent edge, not arbitrary edges to a parent.
---

Directed DFS colours were covered previously. Undirected adjacency lists store each edge at both endpoints, which creates an immediate reverse edge. Here n counts vertices and m counts edges.

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

Two shortcuts. First, a connected undirected graph with no cycle is a tree, and a tree's edge count is fixed by its vertex count:

```formula
m = n − 1
m = 10 − 1 = 9
where
n: the number of vertices in a connected undirected graph; 10 in the example
m: the number of edges
In words: a connected graph is acyclic exactly when it has one edge fewer than it has vertices; any extra edge must close a cycle.
```

So a connected graph with 10 vertices and 10 edges must contain a cycle. The test needs the graph to be connected: a triangle plus one separate, isolated vertex has 4 vertices and 3 edges, one fewer than the vertex count, yet it contains a cycle. Second, Union-Find (lesson 6) detects a cycle the moment an edge joins two vertices already in the same set. The code is presented for simple undirected graphs. In a recursive multigraph DFS, distinguish the particular parent edge by *edge id*: ignoring every edge to the parent can hide a genuine two-edge cycle.

## Pitfalls

- **Directed cycle detection with a visited set**: reports cycles in DAGs (the diamond).
- **Undirected logic on a directed graph** or vice versa: the parent trick is only for undirected graphs.
- **Recursion depth**: a sufficiently long chain can exceed Python’s configured recursion limit. Use iterative versions or `sys.setrecursionlimit` with care.
- **Forgetting disconnected parts**: every algorithm here needs the outer "for each unvisited vertex" loop.

## Key takeaways
- Ignore the particular parent edge, not arbitrary edges to a parent.
- The edge-count tree test requires connected input.

## Further reading
- [Primary reference for this unit](https://networkx.org/documentation/stable/reference/algorithms/cycles.html)
- [Cycle (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Cycle_(graph_theory))
