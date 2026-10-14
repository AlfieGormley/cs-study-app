---
id: graph-all-pairs-selection
title: Sparse all-pairs searches and selected sources
level: intermediate
minutes: 3
sourceLesson: graph-all-pairs
summary: Sparse non-negative graphs often favour repeated single-source searches.
---

BFS handles unit-cost edges; Dijkstra handles non-negative weights; Floyd–Warshall allows negative edges but no finite answer for pairs affected by a negative cycle. Here n counts vertices and m counts edges. Johnson’s negative-edge method is explained next.

## When to run Dijkstra n times instead

APSP with non-negative weights can also be done by running single-source Dijkstra from every vertex.

In the table, n is the number of vertices, m the number of edges and log the base-2 logarithm.

| Method | Time |
|---|---|
| Floyd–Warshall | O(n³) |
| n × Dijkstra (min-heap) | O(n (n + m) log n) |
| n × BFS (unweighted) | O(n (n + m)) |
| Johnson's, binary min-heaps | O(n(n + m) log(n + 1)) |

On a **sparse** graph the edge count is a small multiple of the vertex count, and n Dijkstras win:

```formula
m ≈ cn
n(n + m) log(n)
  ≈ (1 + c)n^2 log(n)
where
n: the number of vertices
m: the number of edges
c: a small constant, the average out-degree; 4 in the example below
log(n): the logarithm of n, base 2
≈: approximately equal to
In words: on a sparse graph n Dijkstras cost about n² log n, which grows much more slowly than Floyd–Warshall's n³.
```

For a road network with ten thousand vertices and forty thousand edges:

```formula
T_FW = n^3 = (10^4)^3 = 10^12
T_D = n(n + m) log_2(n)
T_D ≈ 10^4 × 5 × 10^4 × 13
T_D ≈ 6.5 × 10^9
where
n: the number of vertices; 10^4
m: the number of edges; 4 × 10^4
log_2(n): the base-2 logarithm; log_2(10^4) ≈ 13.3
T_FW: Floyd–Warshall's growth expression
T_D: the growth expression for n runs of min-heap Dijkstra
≈: approximately equal to
In words: Floyd–Warshall's expression is about 150 times larger here.
```

The ratio of these growth expressions is roughly 150; it is not a measured speedup or a count of equivalent machine instructions. On a dense graph (m close to n²) the min-heap version becomes O(n³ log n), worse than Floyd–Warshall.

You also often do not need *all* pairs. If you only need distances between 300 depots in a road graph with ten million vertices, run 300 Dijkstras (or a bidirectional/contraction-hierarchy query per pair) rather than any all-pairs algorithm over the whole road graph.

## Key takeaways
- Sparse non-negative graphs often favour repeated single-source searches.
- Compare growth expressions separately from runtime measurements.
- Compute only the requested sources when a full table is unnecessary.

## Further reading
- [Primary reference for this unit](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
- [Shortest paths — NetworkX docs](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
