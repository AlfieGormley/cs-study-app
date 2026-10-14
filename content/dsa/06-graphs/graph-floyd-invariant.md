---
id: graph-floyd-invariant
title: Floyd–Warshall and its intermediate-vertex invariant
level: intermediate
minutes: 3
sourceLesson: graph-all-pairs
summary: The outer loop unlocks one possible intermediate vertex.
---

Sometimes one source is not enough. A delivery company wants the driving time between every pair of its 300 depots. A network tool wants every router's distance to every other to find the network's **graph diameter** (the longest shortest path). A game precomputes distances between all waypoints so that AI agents can look them up instantly.

That is the **all-pairs shortest paths (APSP)** problem: fill an n × n table where `d[i][j]` is the shortest distance from i to j. Just writing the answer down takes a lot of work:

```formula
N = n^2
N = 300 × 300 = 90000
T = Ω(n^2)
where
n: the number of vertices; 300 depots in the example
N: the number of entries in the distance table, one per ordered pair (i, j)
T: the time of any algorithm that writes the full table
Ω(…): Big Omega: grows at least this fast, up to a constant factor (a lower bound, the mirror image of Big O)
In words: the table has n² entries, so no all-pairs algorithm that writes it out can run faster than about n² steps.
```

For 300 depots that is 90,000 distances. A compressed or query-only representation is a different task. Throughout, m is the number of edges and O(…) is Big O notation: grows at most this fast, up to a constant factor. Assume finite weights and constant-time arithmetic in the complexity bounds below.

## Floyd–Warshall

Floyd–Warshall is a short, elegant piece of **dynamic programming**.

### The idea

Number the vertices 0 to n − 1. The DP table has one layer per number of "unlocked" vertices:

```formula
d_k[i][j]
where
i: the start vertex, a number from 0 to n − 1
j: the end vertex
k: how many vertices are unlocked: only vertices 0 to k − 1 may be used as **intermediate** stops
n: the number of vertices
d_k[i][j]: the shortest distance from i to j using only those intermediate stops
In words: the shortest route from i to j that is allowed to pass through only the first k vertices on the way.
```

- The initial layer allows no intermediates: use minimum direct edge weights, also allowing the zero-length diagonal walk (so a negative graph self-loop can make the diagonal negative), and ∞ for absent connections.
- The final layer allows every vertex: it is the answer.

For the finite shortest-distance recurrence, assume no negative cycles. Going from k to k + 1, we unlock vertex k. A shortest path using intermediates from {0..k} either avoids k (cost dₖ[i][j]) or passes through k exactly once (cost dₖ[i][k] + dₖ[k][j]). So:

```formula
d_{k+1}[i][j] = min(d_k[i][j],
    d_k[i][k] + d_k[k][j])
d_{k+1}[2][1] = min(∞, 5 + 3) = 8
where
i, j: the start and end vertices
k: the vertex being unlocked in this round
d_k[i][j]: the best i→j distance using only vertices 0 to k − 1 as stops
d_{k+1}[i][j]: the best distance once vertex k may also be used
min(…): the smaller of the two values
∞: infinity: no route known yet
In words: the best route from i to j either ignores the newly unlocked vertex k, or goes from i to k and then from k to j.
```

For the worked line, suppose there is an edge 2→0 costing five and an edge 0→1 costing three: before any vertex is unlocked, 2 cannot reach 1, but via vertex 0 it costs 5 + 3 = 8. The code drops the k subscript and updates one table in place.

## Key takeaways
- The outer loop unlocks one possible intermediate vertex.
- Initialise minimum parallel-edge weights and preserve negative self-loops.
- A negative diagonal reveals a negative cycle.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/44sp/)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
