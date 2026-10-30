---
id: graph-dijkstra-assumptions
title: Dijkstra traces, costs and negative edges
level: intermediate
minutes: 4
sourceLesson: graph-shortest-paths
summary: Non-negative weights justify settling the closest unsettled vertex.
---

Earlier Dijkstra code uses heapq and tentative distances, re-pushing an improved vertex and skipping obsolete entries. Here n counts vertices, m counts edges, and edge weights have one common cost unit. The worked trace and correctness proof assume non-negative weights unless explicitly stated otherwise.

### A worked trace

```
S --4--> A --1--> C --3--> T
 \      ^        ^
  1    2        5
   \  /        /
    B --------+
```

Edges: S→A 4, S→B 1, B→A 2, B→C 5, A→C 1, C→T 3.

The table lists nonstale pops; obsolete A(4) and C(6) entries are skipped.

| Pop | dist after relaxing |
|---|---|
| S (0) | A 4, B 1 |
| B (1) | A 3, C 6 |
| A (3) | C 4 |
| C (4) | T 7 |
| T (7) | done |

The direct edge S→A (4) loses to S→B→A (3), and C improves twice. Final: S 0, B 1, A 3, C 4, T 7.

### Why it is correct

When u is popped with the smallest tentative distance, could a cheaper path to u exist? Any such path must leave the settled region somewhere, through some unsettled vertex. That vertex's tentative distance is already at least u's (u was the smallest), and the rest of the path can only add non-negative weight. So no detour can beat u's distance, and it is final.

```formula reference
cost(P) ≥ dist(x) ≥ d
where
P: any path from the source to u
x: the first vertex on P outside the settled region
cost(P): the total weight of P
dist(x): x's tentative distance, which is at most the cost of P's part up to x
d: the tentative distance with which u was popped, the smallest of all unsettled vertices
≥: is at least
In words: any rival path must pass through an unsettled vertex that is already no closer than the vertex just popped, and its remaining edges only add weight, so it cannot be cheaper than the popped distance.
```

The step "the rest of the path can only add weight" is exactly where non-negative weights are needed: a negative edge later on the detour could make it cheaper after all.

### Complexity

Here n is the number of vertices and m the number of edges. An indexed binary min-heap extracts each reachable vertex once and uses decrease-key on improvements. The earlier lazy version can also pop stale entries, with at most one new push per successful edge relaxation. On simple graphs both give the conventional bound O((n + m) log n): about one heap operation per vertex and per edge, each costing time proportional to log n. For a road graph of a million junctions and four million road segments that is on the order of 10⁸ basic steps: a scale estimate, not a measured time.

| Priority queue | Time |
|---|---|
| Binary min-heap | O((n + m) log n) |
| Fibonacci min-heap | O(m + n log n) |
| Unsorted array | O(n²) |

For dense graphs, the O(n²) array bound avoids the binary min-heap bound’s logarithmic factor. Fibonacci min-heaps improve the asymptotic decrease-key bound. Actual speed depends on implementation, successful relaxations and workload; these bounds do not establish a universal winner.

### Why negative edges break it

The correctness argument assumed that extending a path never makes it cheaper. A negative edge breaks exactly that.

```
A --4--> B --2--> D
 \      ^
  5   -3
   \  /
    C
```

1. Pop A: tentative distances are four to B and five to C.
2. Pop B at distance four and settle it: D becomes six.
3. Pop C at distance five: its negative edge improves B to two. But B is already settled and its edge to D has already been used.

Textbook settle-once Dijkstra reports six for D; the true A→C→B→D route costs four.

> [!analogy] Real-world analogy: booking before the cashback offer appears
> You compare train routes and commit to the cheapest fare to each town as you go, on the reasoning that adding more legs can only add to the fare. Then you discover that one pricier route includes a leg with cashback that would have made it the cheapest overall, but you have already booked.
>
> **How it maps:** committing to a town's fare is settling a vertex; "more legs can only cost more" is the non-negative-weight assumption; and the cashback leg is a negative edge, C→B here, which makes a route that looked dearer at the time of settling turn out cheaper.
>
> **Where it stops:** a real traveller could cancel and rebook. Textbook Dijkstra never processes a settled vertex again, so B's outgoing edges are never relaxed with its better distance, and D keeps the wrong distance computed from B's old one.

> [!warning] "My lazy version handled it"
> The lazy-deletion code above *does* re-push B with distance 2 and fixes D, because it never marks vertices as final. That variant gives correct answers with negative edges (but no negative cycles), but a vertex can be re-processed many times, and on adversarial graphs the number of re-processings can grow exponentially with the number of vertices (D. B. Johnson published such graphs in 1973). Use Bellman–Ford instead.

You cannot fix negative edges by adding a constant to every weight either: a path with more edges gets penalised more, which changes which path is shortest.

## Key takeaways
- Non-negative weights justify settling the closest unsettled vertex.
- A lazy min-heap can pop stale entries; its simple-graph bound does not imply a measured winner.
- Constant edge shifts alter paths with different edge counts.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Dijkstra — cp-algorithms](https://cp-algorithms.com/graph/dijkstra.html)
- [Johnson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Johnson%27s_algorithm)
