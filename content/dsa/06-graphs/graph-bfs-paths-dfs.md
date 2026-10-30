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

```formula reference
d = dist(v_front)
d ≤ dist(v_back) ≤ d + 1
where
dist(x): the number of edges from the source to vertex x, as BFS recorded it
x: any vertex
v_front: the vertex at the front of the queue (next to be dequeued)
v_back: the vertex at the back of the queue (most recently enqueued)
d: the distance of the front vertex, which is the layer BFS is currently finishing
≤: is at most
In words: the queue only ever holds vertices from two neighbouring layers: those at the distance BFS is currently finishing at the front, and those one edge further away behind them.
```

In the previous unit's trace, after dequeuing 1 the queue is [2, 3, 4] with distances 1, 2, 2: never more than one apart. So BFS finishes every vertex at one distance before touching any vertex one edge further away. The first time BFS reaches a vertex, it has reached it by the fewest possible edges. The invariant only holds because every edge counts as one step; with different edge costs it breaks.

BFS always minimises edge count. This also minimises total cost when all edges have the same non-negative cost. For unequal non-negative weights use Dijkstra; negative weights need Bellman–Ford or another method covered in the shortest-path units.

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

> [!analogy] Real-world analogy: asking "who told you?"
> News spreads through an office. If everyone remembers who first told them, you can trace any piece of gossip back to its source: ask the last person who told them, then ask that person, and so on until you reach whoever started it.
>
> **How it maps:** "who first told me" is `parent[v]`, the person who started it is the source, and following the chain backwards then reversing it is `path_to`. Because BFS spreads one layer at a time, the first teller is always one step closer to the source, so the chain is a shortest one.
>
> **Where it stops:** office gossip does not spread in tidy layers; someone may hear it first through a long chain while a shorter one exists. BFS's FIFO queue is what guarantees that the first discovery comes by the fewest edges.

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
- Swapping the queue for a stack reorders the exploration; neighbour order affects the trace.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Graph traversal — Wikipedia](https://en.wikipedia.org/wiki/Graph_traversal)
- [Depth-first search — cp-algorithms](https://cp-algorithms.com/graph/depth-first-search.html)
