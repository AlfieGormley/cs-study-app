---
id: graph-flow-augmenting
title: Augmenting paths and Edmonds–Karp
level: advanced
minutes: 4
sourceLesson: graph-advanced
summary: Augment by a residual path’s bottleneck.
---

The preceding unit defined residual edges: unused edge capacity in the forward direction and cancellable backward flow. Its running directed network has s→a 10, s→b 10, a→b 2, a→t 4, a→c 8, b→c 9 and c→t 10. Here n counts vertices and m counts edges.

### Ford–Fulkerson and Edmonds–Karp

**Ford–Fulkerson** is the method: while an augmenting path exists, push its bottleneck edge capacity along it.

- With integer capacities each augmentation adds at least 1, so the number of augmentations is at most the value of the maximum flow, and each search costs O(m). That can be awful if capacities are large: in the classic bad case, paths alternate back and forth across a middle edge with edge capacity 1, needing two million augmentations when the other capacities are a million.
- With irrational capacities a bad path choice may never terminate.

**Edmonds–Karp** fixes the choice: always use the **shortest** augmenting path (fewest edges), found by BFS. That bounds the number of augmentations by the size of the graph, whatever the capacities:

```formula reference
A = O(nm)
T = O(nm) × O(m) = O(nm^2)
where
n: the number of vertices
m: the number of edges
A: the number of augmenting paths Edmonds–Karp uses
T: total running time on the flow-relevant subgraph, where each BFS costs O(m)
O(…): Big O: grows at most this fast, up to a constant factor
In words: the number of shortest augmenting paths grows at most with vertices times edges, and each is found by one BFS over the edges, so the total does not depend on the capacities.
```

So the total is **O(n m²)**, in the unit-cost arithmetic model, independent of how large the edge capacities are. This is a worst-case bound; real runs usually need far fewer augmentations. Integer bit lengths and floating-point error require separate consideration.

```python
from collections import deque, defaultdict

def max_flow(cap, s, t):
    # Exact integer capacities.
    if s == t:
        raise ValueError("same terminals")
    res = defaultdict(dict)
    for u in cap:
        for v, c in cap[u].items():
            if type(c) is not int or c < 0:
                raise ValueError("capacity")
            res[u][v] = res[u].get(v, 0) + c
            # reverse edge, initially 0
            # Cancellation needs a reverse
            # residual.
            res[v].setdefault(u, 0)
    flow = 0
    while True:
        par = {s: None}
        q = deque([s])
        while q and t not in par:
            # FIFO order finishes earlier
            # layers.
            u = q.popleft()
            for v, c in res[u].items():
                if c > 0 and v not in par:
                    par[v] = u
                    q.append(v)
        if t not in par:
            return flow, res
        b, v = float('inf'), t
        while par[v] is not None:
            # Bottleneck limits the whole
            # augmentation.
            b = min(b, res[par[v]][v])
            v = par[v]
        v = t
        while par[v] is not None:
            u = par[v]
            # Consume forward residual
            # capacity.
            res[u][v] -= b
            # Enable cancellation of the new
            # flow.
            res[v][u] += b
            v = u
        flow += b
```

On the first example it returns `(14, residual_graph)`: the flow value and the final residual capacities.

> [!note] Faster algorithms
> **Dinic's algorithm** pushes many shortest paths at once using BFS levels and DFS blocking flows: O(n²m) in general and O(m√n) (√ is the square root; n vertices, m edges) on unit networks such as the standard bipartite matching reduction. Arbitrary unit-capacity networks need a different bound; edge capacity 1 alone does not establish O(m√n). Push-relabel is another family whose performance depends on the instance and implementation.

A useful fact: with integer capacities there is always an **integer** maximum flow, and these algorithms find one. This is what makes flow usable for counting and assignment problems.

## Key takeaways
- Augment by a residual path’s bottleneck.
- Shortest augmenting paths bound the number of searches independently of edge capacity magnitude.
- Exact integer capacities avoid the floating-point complications omitted here.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 6.4 Maximum flow](https://algs4.cs.princeton.edu/64maxflow/)
- [Max-flow min-cut theorem — Wikipedia](https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem)
- [Ford–Fulkerson algorithm — Wikipedia](https://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm)
