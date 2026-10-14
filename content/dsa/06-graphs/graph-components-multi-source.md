---
id: graph-components-multi-source
title: Components, flood fill and multiple sources
level: basic
minutes: 4
sourceLesson: graph-bfs-dfs
summary: Start traversals from every unvisited vertex to include all components.
---

These applications reuse BFS and DFS. The recursive dfs(adj, u, seen) routine from the earlier tracing unit marks u and explores unseen neighbours. Import deque from collections for the BFS fragment below. Every vertex, including isolates, must have an adjacency entry.

## Connected components

A traversal from s finds everything reachable from s. To find *every* component of an undirected graph, loop over all vertices and start a new traversal from each unvisited one.

```python
def components(n, adj):
    seen = set()
    count = 0
    for v in range(n):
        if v not in seen:
            # One new traversal means one
            # component.
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
W_separate = O(k(n + m))
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

With 500 hospitals on an unweighted road graph, that is the difference between 500 traversals and one; unequal travel times require a weighted shortest-path method. So **put all sources in the queue at distance 0** and run one BFS.

```python
def nearest(adj, sources):
    # Seed all sources in the first layer.
    dist = {s: 0 for s in sources}
    q = deque(dist)
    while q:
        # FIFO order finishes earlier
        # layers.
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                # Every move adds one edge
                # of distance.
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

## Pitfalls

- **Forgetting the visited set** on a graph with cycles: the traversal loops forever.
- **Using DFS for "fewest steps".** DFS finds *a* path, not the shortest.
- **`list.pop(0)` as a queue** is O(n) per pop in Python, where n is the current queue length, because every remaining item moves one place left. Use `collections.deque`.
- **Missing disconnected parts.** A single traversal only covers one component.

## Key takeaways
- Start traversals from every unvisited vertex to include all components.
- Seed every source at distance zero to find the nearest one in a single BFS.

## Further reading
- [Primary reference for this unit](https://networkx.org/documentation/stable/reference/algorithms/component.html)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Component (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Component_(graph_theory))
