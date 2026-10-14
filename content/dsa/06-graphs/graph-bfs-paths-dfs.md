---
id: graph-bfs-paths-dfs
title: Recovering BFS paths and tracing DFS
level: basic
minutes: 3
sourceLesson: graph-bfs-dfs
summary: BFS parent pointers recover a shortest unweighted path.
---

The previous unit’s BFS returns a distance dictionary and parent pointers. In its running example the adjacency lists are 0:[1,2], 1:[0,3,4], 2:[0,4], 3:[1], 4:[1,2,5], 5:[4]. The source is vertex 0. Here n counts vertices and m counts edges. BFS distances count edges.

### Why BFS finds shortest paths

The key fact is an invariant (a rule that stays true at every step) about what the queue holds:

```formula
d = dist(v_front)
d ≤ dist(v_back) ≤ d + 1
where
dist(x): the number of edges from the source to vertex x, as BFS recorded it
x: any vertex
v_front: the vertex at the front of the queue (next to be dequeued)
v_back: the vertex at the back of the queue (most recently enqueued)
d: the distance of the front vertex, which is the layer BFS is currently finishing
≤: is at most
In words: the queue only ever holds vertices from two neighbouring layers, distance d at the front and d + 1 behind them, in that order.
```

In the trace above, after dequeuing 1 the queue is [2, 3, 4] with distances 1, 2, 2: never more than one apart. So BFS finishes every vertex at distance d before touching any at distance d + 1. The first time BFS reaches a vertex, it has reached it by the fewest possible edges. The invariant only holds because every edge counts as one step; with different edge costs it breaks.

BFS always minimises edge count. This also minimises total cost when all edges have the same non-negative cost. For unequal non-negative weights use Dijkstra; negative weights require additional care (lesson 4).

To recover the actual path, follow `parent` pointers back from the target and reverse:

```python
def path_to(parent, t):
    if t not in parent:
        return None
    path = []
    while t is not None:
        path.append(t)
        t = parent[t]
    # Reverse target-to-source links.
    return path[::-1]

# path_to(parent, 5) -> [0, 1, 4, 5]
```

## Depth-first search

DFS uses a **stack**, either the call stack (recursion) or an explicit list.

```python
def dfs(adj, u, seen):
    # Mark before exploring more neighbours.
    seen.add(u)
    for v in adj[u]:
        if v not in seen:
            dfs(adj, v, seen)
```

From 0 the recursive version visits 0, 1, 3, 4, 2, 5. It dives 0→1→3, hits a dead end, backs up to 1, goes to 4, then 2 (whose neighbours are all seen), backs up to 4, then 5.

```
dfs(0)
 └ dfs(1)
    ├ dfs(3)
    └ dfs(4)
       ├ dfs(2)
       └ dfs(5)
```

The iterative version avoids Python's configurable recursion-depth limit, which a long chain easily exceeds:

```python
def dfs_iter(adj, s):
    seen, order = set(), []
    stack = [s]
    while stack:
        # Explore the last pending branch
        # first.
        u = stack.pop()
        # Discard duplicate pending
        # discoveries.
        if u in seen:
            continue
        # Mark before exploring more
        # neighbours.
        seen.add(u)
        # Record actual processing order.
        order.append(u)
        for v in adj[u]:
            if v not in seen:
                stack.append(v)
    return order
```

This one visits 0, 2, 4, 5, 1, 3. It is still a valid DFS, but the order differs because the *last* neighbour pushed is popped first. Push neighbours in reverse if you need the recursive order. Note that here the `seen` check happens on pop, so a vertex may sit on the stack more than once; that is fine and still O(n + m) overall, where n is the number of vertices and m the number of edges.

## Key takeaways
- BFS parent pointers recover a shortest unweighted path.
- A stack changes the exploration order; neighbour order affects the trace.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Graph traversal — Wikipedia](https://en.wikipedia.org/wiki/Graph_traversal)
- [Depth-first search — cp-algorithms](https://cp-algorithms.com/graph/depth-first-search.html)
