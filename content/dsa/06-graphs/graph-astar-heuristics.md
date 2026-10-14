---
id: graph-astar-heuristics
title: Admissible, consistent and weighted heuristics
level: intermediate
minutes: 3
sourceLesson: graph-shortest-paths
summary: Admissibility and consistency make different guarantees.
---

A* ranks vertices using known cost plus a heuristic estimate; these quantities and edge weights share one cost unit. A heuristic’s guarantee depends on the graph and movement rules, not its name alone.

### Heuristic quality

For finite graphs with non-negative edge costs, a zero heuristic at the reachable goal, and a heuristic expressed in the same cost units, two properties matter:

```formula
h(v) ≤ h*(v)
h(u) ≤ w(u, v) + h(v)
where
h(v): the heuristic estimate of the remaining cost from v to the goal
h*(v): the true cheapest remaining cost from v to the goal
u, v: the two ends of an edge u→v
w(u, v): the weight of that edge
≤: is at most
In words: the first line (admissible) says the guess never overestimates; the second (consistent) says the guess never drops by more than the cost of the edge you just took.
```

For example, Manhattan distance on a 4-way grid with cost-1 moves is consistent: one move changes it by at most 1, the cost of the move.

- **Admissible**: h never overestimates the true remaining cost (the first line). A* that reopens a vertex when a better g is found and stops when the goal is popped returns an optimal path. Merely discovering the goal is not a safe stopping condition.
- **Consistent heuristic** (monotone): the second line holds for every edge. With a zero heuristic at the goal this implies admissibility, and no settled vertex needs reopening.
- A **zero heuristic** gives Dijkstra’s ordering. A **perfect-distance heuristic** can still expand many vertices lying on different optimal paths; ties matter.

| Movement | Admissible h |
|---|---|
| 4-way grid, cost 1 | Manhattan |
| 8-way grid, straight cost 1 and diagonal cost the square root of 2 | Octile |
| 8-way grid, all moves cost 1 | Chebyshev |
| Geometric edges costing at least their Euclidean length | Euclidean |
| Travel time with a valid global speed upper bound | Straight-line distance ÷ that speed |

> [!tip] Trading optimality for speed
> **Weighted A* search** inflates the heuristic to search more greedily towards the goal. It can reduce expansions, but a speedup is not guaranteed. The price is a bounded loss of optimality, shown below.

On a finite graph with non-negative costs, an admissible heuristic that is zero at the goal, reopening on improved known cost, and stopping when the goal is popped, weighted A* returns a cost within a known factor of the best:

```formula
f(v) = g(v) + λ h(v)
C ≤ λ C*
C ≤ 1.5 × 100 = 150
where
v: a vertex in the min-heap
f(v): its priority; the min-heap pops the smallest
g(v): the known cost from the start to v
h(v): the heuristic estimate of the remaining cost to the goal
λ: the inflation weight, greater than 1; 1.5 in the example
C: the cost of the path weighted A* returns
C*: the cost of the true shortest path; 100 in the example
In words: weighting the heuristic by λ can make the answer at most λ times the optimum.
```

With an inflation factor of 1.5 and a true shortest cost of 100, the path found costs at most 150.

Route-planning methods include contraction hierarchies and landmark heuristics (ALT).

> [!note] Content gap
> Product-specific implementations and millisecond/vertex-count performance claims are omitted: no identified dataset, implementation and reproducible measurement support them here.

## Key takeaways
- Admissibility and consistency make different guarantees.
- Stop on a popped goal, with the stated reopening policy.
- Weighted A* trades an optimality bound for more goal-directed ordering.

## Further reading
- [Primary reference for this unit](https://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/astar.pdf)
- [Admissible heuristic — Wikipedia](https://en.wikipedia.org/wiki/Admissible_heuristic)
- [A* search algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Thayer and Ruml: Faster Than Weighted A*](https://cdn.aaai.org/ICAPS/2008/ICAPS08-044.pdf)
