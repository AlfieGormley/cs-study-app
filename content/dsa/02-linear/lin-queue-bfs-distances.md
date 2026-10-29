---
id: lin-queue-bfs-distances
title: A FIFO frontier finds unweighted distances
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: Enqueue newly discovered nodes once and record their distance immediately.
---

A FIFO queue processes older discoveries before newer ones. That order gives shortest edge-count distances in an unweighted graph. Use the deque import shown below; each neighbour in the example must also be a key in the adjacency mapping.

## Queues in BFS

**Breadth-first search** explores a graph in rings: all nodes one edge away, then two, then three. A queue enforces exactly that order, because nodes discovered earlier (closer) are processed before nodes discovered later (further).

```python
from collections import deque

def bfs(graph, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        # Process the oldest discovered
        # node.
        node = q.popleft()
        for nb in graph[node]:
            if nb not in dist:
                # Mark discovery before
                # enqueueing.
                dist[nb] = dist[node] + 1
                q.append(nb)
    return dist
```

> [!analogy] Real-world analogy: Ripples from a stone
> Drop a stone in a still pond and the ripples spread outwards in rings: everything one step away is reached before anything two steps away.
>
> **How it maps:** The stone is `start`, each ring is one more edge of distance, and the queue holds the expanding front of the ripple. Because the queue serves older discoveries first, the whole of one ring is processed before the next ring begins.
>
> **Where it stops:** Ripples spread continuously and in every direction at once, while BFS processes one node at a time and only along edges. The ring picture also assumes every edge has the same length; weighted graphs need a different algorithm.

In an **unweighted graph**, `dist` is the shortest number of edges from `start` to every reachable node. Replacing the queue with a stack removes the shortest-path guarantee. With discovery marked on push, it is a LIFO traversal but does not necessarily reproduce recursive DFS discovery/parent order; standard DFS uses an appropriate marking or iterator-stack strategy. Graph traversal gets a full treatment in the graphs module.

> [!warning] Mark nodes when you enqueue them
> Mark a node as seen when it's **added** to the queue, not when it's removed. Otherwise the same node can be enqueued many times by different neighbours, blowing up time and memory on dense graphs.

### Two routes to the same node

Suppose A discovers B and C; both lead to D, while C also leads to E. D and E both lead to F. Starting at A, the queue processes A, B, C, D, E, F when neighbours are listed in that order.

D is marked when B enqueues it, so C does not enqueue it again. F is similarly discovered once. Its shortest distance is three edges: the queue has processed every one-edge and two-edge discovery before a three-edge node can be removed.

This claim depends on equal edge cost. A weighted edge cannot be represented merely by one queue step; weighted shortest paths require another strategy. The returned mapping covers only reachable nodes, and a missing adjacency key raises KeyError in this compact teaching implementation. Graph representation, traversal complexity and weighted shortest paths are explored in later modules.

## Key takeaways
- Enqueue newly discovered nodes once and record their distance immediately.
- FIFO exploration processes reachable nodes in nondecreasing unweighted distance.

## Further reading
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
