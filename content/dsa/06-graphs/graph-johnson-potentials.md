---
id: graph-johnson-potentials
title: Johnson potentials and path-preserving reweighting
level: intermediate
minutes: 3
sourceLesson: graph-all-pairs
summary: Bellman–Ford potentials make reweighted edges non-negative.
---

Earlier units covered Bellman–Ford’s negative-cycle test and Dijkstra’s non-negative-weight requirement. Here n counts vertices and m counts edges. Graphs and weights are finite, with constant-time arithmetic assumed for the growth bounds.

## Johnson's algorithm: negative edges on sparse graphs

Dijkstra cannot handle negative edges, and Floyd–Warshall is O(n³). Johnson's algorithm gets the best of both:

1. Add a new vertex q with a 0-weight edge to every vertex.
2. Run **Bellman–Ford** from q to get h(v) for each v (O(n(n + m)) for the augmented graph). If it finds a negative cycle, stop.
3. **Reweight** each edge by adding the potential of its start and subtracting the potential of its end (formula below). Because the potentials are shortest-path distances, every new weight is non-negative.
4. Run **Dijkstra** from every vertex on w'.
5. Undo the shift on each answer.

Steps 3 and 5 in full:

```formula essential
h(v) ≤ h(u) + w(u, v)
w'(u, v) = w(u, v) + h(u) − h(v) ≥ 0
d(u, v) = d'(u, v) − h(u) + h(v)
where
u, v: two vertices; in the first two lines, the ends of an edge u→v
w(u, v): the original weight of edge u→v, possibly negative
h(x): the potential of vertex x: its shortest distance from q, found by Bellman–Ford; never positive, because q reaches x by a 0-weight edge
x: any vertex
w'(u, v): the reweighted edge, never negative
d'(u, v): the shortest u→v distance Dijkstra finds with the new weights
d(u, v): the true shortest distance with the original weights
≤: is at most
≥: is at least
In words: shortest distances obey the triangle inequality, so adding the potential difference makes every edge non-negative, and subtracting it at the end restores the true distances.
```

For example, an edge of weight minus three from a vertex with potential zero to one with potential minus three is reweighted to −3 + 0 − (−3) = 0.

Why step 3 preserves shortest paths: along any path u → x₁ → … → v, each middle potential is added once and subtracted once, so the h terms telescope (cancel in pairs) and every u→v path changes by exactly h(u) − h(v). The ranking of paths is unchanged. (Compare adding a constant to every edge, which penalises long paths more and breaks the ranking.)

> [!analogy] Real-world analogy: height gained on a hill walk
> On a hill walk, the total height you gain minus the height you lose depends only on where you start and finish, not on the route: every intermediate climb you make, you later descend, or vice versa.
>
> **How it maps:** a vertex's potential is like an altitude, and each reweighted edge adds its start altitude minus its end altitude to its original cost. Over any route from u to v the intermediate altitudes cancel, so every route between the same two vertices gets the same adjustment, and the cheapest route stays the cheapest.
>
> **Where it stops:** the potentials are shortest-path distances from the extra vertex, not real heights, and they are chosen specifically so that every reweighted edge comes out non-negative. Ordinary altitudes would cancel in the same way but would not guarantee that.

With binary min-heaps on simple graphs, total time is O(n(n + m) log(n + 1)), including the augmented Bellman–Ford run. When the edge count grows at least proportionally to the vertex count, this is commonly simplified to O(nm log n).

## Key takeaways
- Bellman–Ford potentials make reweighted edges non-negative.
- Intermediate potentials cancel along a path.
- Recover original distances after running Dijkstra.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Johnson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Johnson%27s_algorithm)
