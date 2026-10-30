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

> [!analogy] Real-world analogy: seating guests who are feuding
> A host has two tables and a list of pairs of guests who must not sit together. If Ann feuds with Ben, and Ben with Cal, then Ann and Cal must share a table. Trouble comes only when the feuds go round in a loop of odd length: three people who all feud with each other cannot be split between two tables.
>
> **How it maps:** guests are vertices, feuds are edges, and the two tables are the two colours. A seating plan that works is a 2-colouring, and an odd loop of feuds is an odd cycle, the one thing that makes it impossible.
>
> **Where it stops:** a host can add a third table. Bipartiteness is specifically about two sides, and it is decided entirely by odd cycles; deciding whether three colours suffice is a much harder problem.

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

BFS colours by layer parity: vertices an even number of edges from the start of their component go on one side, odd ones on the other. For example, a vertex 3 edges from the start gets colour 1. A clash means an edge inside one layer, or between two layers of equal parity, which closes an odd cycle. The check costs O(n + m) for n vertices and m edges, and the outer loop handles disconnected graphs.

## Key takeaways
- Colour every component, not just the one containing the first vertex.
- A same-colour edge proves that the undirected graph is not bipartite.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Bipartite graph — Wikipedia](https://en.wikipedia.org/wiki/Bipartite_graph)
