---
id: graph-min-cut-certificates
title: Minimum cuts and upgrade certificates
level: advanced
minutes: 3
sourceLesson: graph-advanced
summary: A cut upper-bounds every feasible flow.
---

The previous two units introduced feasible flow and residual cancellation. The example network is s→a 10, s→b 10, a→b 2, a→t 4, a→c 8, b→c 9 and c→t 10. Its feasible maximum flow is 14. Capacities and flows share the same throughput unit.

## Max-flow min-cut

An **s–t cut** splits the vertices into S (containing s) and T (containing t). Its **cut capacity** is the total edge capacity of edges going **from S to T** (edges from T back to S do not count):

```formula reference
K(S, T) = Σ cap(u, v)
|f| ≤ K(S, T)
where
S: the set of vertices on the source side, including s
T: the set on the sink side, including t
u, v: the ends of an edge u→v that goes from S to T
cap(u, v): edge capacity of edge u→v, in the chosen throughput units
K(S, T): cut capacity, in the same units
|f|: the value of any flow
Σ: add capacities over every edge from S to T
≤: is at most
In words: a cut's capacity is the total edge capacity of the edges crossing from the source side to the sink side, and no flow can exceed it, because every unit of flow must make that crossing.
```

For example, placing s, a, b and c on the source side and only t on the sink side gives a cut whose forward edges are a→t (4) and c→t (10): cut capacity 14.

> [!analogy] Real-world analogy: checkpoints on a boundary line
> Draw any boundary line that separates a factory from its warehouse. Every lorry that makes the journey must cross that line somewhere, so the combined throughput of the crossing points on that line caps the daily deliveries, wherever you draw it.
>
> **How it maps:** the factory is s, the warehouse is t, a boundary line is an s–t cut and the crossing points are the edges from the source side to the sink side. The tightest line you can draw is the minimum cut, and the theorem says the best delivery plan exactly fills it.
>
> **Where it stops:** real lorries can cross a line, come back and cross again. In a cut only the edge capacity of edges going from the source side to the sink side counts; edges coming back do not add to it.

> [!note] Max-flow min-cut theorem
> The maximum flow value equals the smallest cut capacity over all s–t cuts.

The intuition: every unit of flow must cross every cut, so the flow value is at most any cut capacity. When Ford–Fulkerson stops, let S be the vertices still reachable from s in the residual graph. Every edge S→T is a saturated edge, full to its edge capacity (or it would be in the residual), and every edge T→S carries 0 (or its backward residual would be usable). So the flow equals that cut capacity, and both are optimal.

In the first example, after the algorithm finishes, s, a, b and c lie on the source side, with only t on the sink side. The cut edges are a→t (4) and c→t (10): cut capacity **14**, matching the flow. Increasing only links outside this cut cannot raise the maximum flow while its cut capacity stays 14. Other engineering objectives or coordinated upgrades can still justify those changes.

Uses of min cut:

- **Image segmentation**: pixels are vertices, the source means "foreground", the sink "background", and edge capacities penalise cutting between similar neighbours. The min cut optimises the specified representable segmentation energy (the basis of "graph cuts" in computer vision).
- **Network reliability**: the minimum number of links whose failure disconnects two data centres equals the max flow with unit capacities.
- **Baseball elimination** and **project selection** reduce neatly to min cut.

## Key takeaways
- A cut upper-bounds every feasible flow.
- Residual reachability yields a matching optimal cut after augmentation stops.
- Upgrading an edge outside a still-tight cut cannot increase the maximum flow.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 6.4 Maximum flow](https://algs4.cs.princeton.edu/64maxflow/)
- [Maximum flow problem — Wikipedia](https://en.wikipedia.org/wiki/Maximum_flow_problem)
- [Max-flow min-cut theorem — Wikipedia](https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem)
