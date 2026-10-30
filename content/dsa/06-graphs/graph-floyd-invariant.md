---
id: graph-floyd-invariant
title: Floyd–Warshall and its intermediate-vertex invariant
level: intermediate
minutes: 3
sourceLesson: graph-all-pairs
summary: The outer loop unlocks one possible intermediate vertex.
---

Sometimes one source is not enough. A delivery company wants the driving time between every pair of its 300 depots. A network tool wants every router's distance to every other to find the network's **graph diameter** (the longest shortest path). A game precomputes distances between all waypoints so that AI agents can look them up instantly.

That is the **all-pairs shortest paths (APSP)** problem: fill an n × n table where `d[i][j]` is the shortest distance from i to j, for n vertices. Just writing the answer down takes a lot of work: one entry per ordered pair, so 90,000 distances for 300 depots, and no algorithm that writes out the full table can take fewer than about n² steps. A compressed or query-only representation is a different task.

Throughout, m is the number of edges and O(…) is Big O notation: grows at most this fast, up to a constant factor. Assume finite weights and constant-time arithmetic in the complexity bounds below.

## Floyd–Warshall

Floyd–Warshall is a short, elegant piece of **dynamic programming**.

### The idea

Number the vertices 0 to n − 1. Instead of asking for the best route straight away, ask a smaller question first: what is the best route from i to j if only some vertices are allowed as **intermediate stops** (the vertices strictly between the start and the end)?

- At the start no intermediate stops are allowed. The table holds the direct edge weights (the lightest one, if there are parallel edges), zero for each vertex to itself (lower if a negative graph self-loop exists) and ∞ for pairs with no edge.
- Then vertex 0 is unlocked as a possible stop, then vertex 1, and so on.
- Once every vertex is unlocked, the table holds the true shortest distances.

Assume no negative cycles for the finite recurrence. When vertex k is unlocked, a best route from i to j that may now use k either avoids k, so it is the old answer, or passes through k exactly once, so it is the best route from i to k followed by the best route from k to j, both using only the earlier stops:

```formula essential
d_{k+1}[i][j] = min(d_k[i][j],
    d_k[i][k] + d_k[k][j])
where
i, j: the start and end vertices
k: the vertex being unlocked in this round
d_k[i][j]: the best i→j distance using only vertices 0 to k − 1 as intermediate stops
d_{k+1}[i][j]: the best distance once vertex k may also be used
min(…): the smaller of the two values
In words: the best route from i to j either ignores the newly unlocked vertex k, or goes from i to k and then from k to j.
```

For example, suppose there is an edge 2→0 costing five and an edge 0→1 costing three. Before any vertex is unlocked, 2 cannot reach 1; once vertex 0 is unlocked, 2 reaches 1 for 5 + 3 = 8. The code in the next unit drops the k subscript and updates one table in place.

> [!analogy] Real-world analogy: opening interchange stations one at a time
> Imagine a rail network where, at first, you may only take direct trains. Then one station at a time is opened as an interchange. Each time a new interchange opens, you check every journey: is it now quicker to change trains there than to use the best route you had?
>
> **How it maps:** stations are vertices, the journey-time table is `d`, and opening an interchange is one round of the outer loop that unlocks vertex k. The check for each journey is the recurrence: keep the old time, or go to the new interchange and on from there.
>
> **Where it stops:** a real route may change trains at several interchanges, and Floyd–Warshall handles that only because each round builds on the table from the previous rounds; the order in which stations open does not change the final table, but every pair must be rechecked in every round. Real timetables also add waiting times at interchanges, which plain edge weights do not model.

## Key takeaways
- The outer loop unlocks one possible intermediate vertex.
- Initialise minimum parallel-edge weights and preserve negative graph self-loops.
- After every vertex is unlocked, the table holds all shortest distances.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
