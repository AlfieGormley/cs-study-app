---
id: adv-dsu-graph-applications
title: Kruskal and incremental connectivity
level: intermediate
minutes: 3
summary: Kruskal accepts exactly the edges that join different components.
sourceLesson: adv-union-find
---

## Application 1: Kruskal's minimum spanning tree

Kruskal's algorithm builds a minimum spanning tree by taking edges cheapest first and keeping an edge only if it joins two different components. "Different components?" is exactly `find(u) != find(v)`, and keeping the edge is `union(u, v)`.

```python
def kruskal(n, edges):
    # edges: list of (weight, u, v)
    dsu = DSU(n)
    total, used = 0, []
    for w, u, v in sorted(edges):
        # Keep edges only between
        # components.
        if dsu.union(u, v):
            total += w
            used.append((u, v))
    return total, used
```

For V vertices and E unsorted edges, initialising the DSU takes O(V), comparison-sorting the edges takes O(E log E), and processing them takes O(E α(V)) with balancing and compression. Sorting dominates for a connected graph; if a disconnected graph has many isolated vertices, initialisation can matter instead.

On disconnected input the code returns a minimum spanning forest. In a connected graph you can stop once the chosen edges connect every vertex: the tree then has one fewer edge than vertices.

## Application 2: connectivity and cycle detection

- Number of connected components: start with `count = n` and decrement on every successful union. Edges can arrive one at a time ("number of islands II", or a network where links come up over time), and you can answer after each one.
- **Cycle detection in an undirected graph**: adding edge (u, v) when `find(u) == find(v)` closes a cycle. `union` returning `False` is the signal. This is the "redundant connection" problem.
- **Percolation**: a grid percolates when a virtual top node and a virtual bottom node end up in the same set, a classic Monte Carlo experiment.

Compared with BFS or DFS, union-find shines when edges arrive incrementally. A straightforward BFS test of graph reachability may traverse the current graph for each request; union-find just absorbs each new edge.

## Key takeaways

- Kruskal accepts exactly the edges that join different components.
- A failed union detects a cycle in an undirected incremental graph.

## Further reading
- [Disjoint-set unions — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
