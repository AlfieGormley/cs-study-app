---
id: graph-zero-one-choice
title: 0–1 BFS and choosing a shortest-path method
level: intermediate
minutes: 2
sourceLesson: graph-shortest-paths
summary: A zero-weight improvement goes to the front of the deque.
---

Earlier units covered unweighted BFS, Dijkstra and Bellman–Ford. Here n counts vertices and m counts edges. INF in the snippet is float("inf"). A* in the comparison table is introduced in the next two units; its heuristic is an estimate of remaining cost.

## 0-1 BFS

If every weight is **0 or 1**, you do not need a min-heap. Use a **deque**: push to the front for a 0-edge (same distance) and to the back for a 1-edge (one more).

```python
from collections import deque

def zero_one_bfs(adj, s):
    # Zero distance also marks discovery.
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
                    # A free edge stays in
                    # the same layer.
                    dq.appendleft((nd, v))
                else:
                    # Cost one goes behind
                    # the current layer.
                    dq.append((nd, v))
    return dist
```

Queued distance labels occupy at most two consecutive values in nondecreasing order; obsolete entries are skipped. Thus, it behaves like Dijkstra's min-heap at O(1) per operation: **O(n + m)** total, for n vertices and m edges.

Typical problems: the fewest walls to break in a maze (stepping into a wall costs 1, open floor 0), or a grid where following the printed arrow is free and changing direction costs 1.

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
- A zero-weight improvement goes to the front of the deque.
- Match edge-weight assumptions to the algorithm before comparing costs.

## Further reading
- [0-1 BFS — cp-algorithms](https://cp-algorithms.com/graph/01_bfs.html)
