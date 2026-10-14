---
id: graph-bipartite-colouring
title: Bipartite graphs and odd cycles
level: intermediate
minutes: 2
sourceLesson: graph-dfs-applications
summary: Colour every component, not just the one containing the first vertex.
---

BFS visits successive distance layers. Import deque from collections for the following function. Here n counts vertices and m counts edges; adjacency lists include every vertex and both directions of every undirected edge.

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
            # FIFO order finishes earlier
            # layers.
            u = q.popleft()
            for v in adj[u]:
                if color[v] is None:
                    # Neighbours must belong
                    # to opposite sides.
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
```

BFS colours by layer parity (whether the layer number is even or odd):

```formula
colour(v) = dist(v) mod 2
where
v: any vertex
dist(v): v's BFS distance from the start of its component, in edges
mod 2: the remainder after dividing by 2: 0 for even, 1 for odd
colour(v): the side v is put on, 0 or 1
In words: even layers go on one side and odd layers on the other.
```

For example, a vertex 3 edges from the start gets colour 1. A clash means an edge inside one layer, or between two layers of equal parity, which closes an odd cycle. The check costs O(n + m) for n vertices and m edges, and the outer loop handles disconnected graphs.

## Key takeaways
- Colour every component, not just the one containing the first vertex.
- A same-colour edge proves that the undirected graph is not bipartite.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Bipartite graph — Wikipedia](https://en.wikipedia.org/wiki/Bipartite_graph)
