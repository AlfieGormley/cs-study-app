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

Here V is the number of vertices and E the number of edges. The three phases add up:

```formula
T = O(V) + O(E log(E)) + O(E α(V))
T_c = O(E log(E))
E ≥ V − 1
E log_2(E) ≈ 10,000 × 13.3 ≈ 133,000
E α(V) = 10,000 × 4 = 40,000
where
T: the total running time of Kruskal's algorithm
T_c: the total running time when the graph is connected (every vertex reachable from every other) and V ≥ 2
V: the number of vertices (nodes) in the graph
E: the number of edges in the graph
log(E): the logarithm of E; the base only changes a constant factor
log_2(E): the base-2 logarithm of E, about the number of comparison rounds a good sort needs per edge
α(V): the inverse Ackermann function of V, at most 4 in practice
O(f): "grows at most in proportion to f"
≥: is at least
≈: approximately equal to
In words: initialising the DSU, sorting the edges and processing them add up, and on a connected graph sorting the edges is the part that dominates.
```

A connected graph needs at least one edge fewer than it has vertices (the third line), so the sort outgrows both other terms. The last two lines are a worked example with 1,000 vertices and 10,000 edges: illustrative scaling terms near 133,000 for sorting and 40,000 for DSU processing. These are substitutions into growth models, not predicted comparison or pointer-step counts; each union includes two finds and the constants differ. Disconnected graphs may instead be dominated by initialisation; the code returns a minimum spanning forest. You can stop early once `used` has one fewer edge than the graph has vertices.

## Application 2: connectivity and cycle detection

- Number of connected components: start with `count = n` and decrement on every successful union. Edges can arrive one at a time ("number of islands II", or a network where links come up over time), and you can answer after each one.
- **Cycle detection in an undirected graph**: adding edge (u, v) when `find(u) == find(v)` closes a cycle. `union` returning `False` is the signal. This is the "redundant connection" problem.
- **Percolation**: a grid percolates when a virtual top node and a virtual bottom node end up in the same set, a classic Monte Carlo experiment.

Compared with BFS or DFS, union-find shines when edges arrive incrementally. A straightforward BFS test of graph reachability may traverse the current graph for each request; union-find just absorbs each new edge.

## Key takeaways

- Kruskal accepts exactly the edges that join different components.
- A failed union detects a cycle in an undirected incremental graph.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
