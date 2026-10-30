---
id: graph-bfs-layers
title: Breadth-first layers and queue discipline
level: basic
minutes: 4
sourceLesson: graph-bfs-dfs
summary: BFS expands a FIFO queue in increasing edge-distance layers.
---

Almost every graph algorithm is a traversal in disguise. There are two basic ways to explore a graph from a starting vertex:

- **Breadth-first search (BFS)** spreads out like a ripple in a pond: first everything 1 step away, then everything 2 steps away, and so on.
- **Depth-first search (DFS)** behaves like someone in a maze trailing a ball of twine: go as deep as possible down one corridor, and only back up when you hit a dead end.

Throughout this lesson, n is the number of vertices and m the number of edges. Both traversals touch each vertex and each edge a bounded number of times, so one full traversal costs O(n + m): work proportional to vertices plus edges, so doubling the graph roughly doubles the time. This assumes adjacency lists and the usual constant-time access model; dictionary and set bounds here are expected bounds. All referenced vertices must have adjacency entries.

What differs between BFS and DFS is the *order*, and that order is what makes each one useful.

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
    # Zero distance also marks discovery.
    dist = {s: 0}
    parent = {s: None}
    q = deque([s])
    while q:
        # FIFO order finishes earlier
        # layers.
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                # Every move adds one edge
                # of distance.
                dist[v] = dist[u] + 1
                # Remember which predecessor
                # found v.
                parent[v] = u
                q.append(v)
    # Return lengths and reconstruction
    # links.
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

### Mark when you enqueue, not when you dequeue

> [!warning] A classic bug
> If you mark a vertex visited only when it is *dequeued*, it can be enqueued many times by different neighbours before it is processed. On a dense graph the queue can grow to O(m) entries (in proportion to m, the number of edges), and some versions compute wrong distances. Mark (or set `dist`) at the moment you enqueue.

BFS answers plain reachability and fewest unit-cost knight moves on an implicit chessboard graph. It does not minimise unequal road lengths or find a longest simple path in a general graph; the latter problem is NP-hard.

## Key takeaways
- BFS expands a FIFO queue in increasing edge-distance layers.
- Record discovery when enqueuing to prevent duplicate queue entries.

## Further reading
- [Python docs: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Breadth-first search — cp-algorithms](https://cp-algorithms.com/graph/breadth-first-search.html)
- [Shortest path problem — Wikipedia](https://en.wikipedia.org/wiki/Shortest_path_problem)
