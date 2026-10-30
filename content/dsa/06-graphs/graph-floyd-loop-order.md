---
id: graph-floyd-loop-order
title: Implementing Floyd–Warshall in the right order
level: intermediate
minutes: 2
sourceLesson: graph-all-pairs
summary: Keep the intermediate vertex loop outermost.
---

Earlier units defined the distance table by permitted intermediate vertices. Here n counts vertices and m counts edges. The recurrence below assumes no negative cycles; affected pairs need the separate interpretation covered next.

The worked graph used in this unit’s loop-order question has edges 0→1 3, 0→3 7, 1→0 8, 1→2 2, 2→0 5, 2→3 1 and 3→0 2. A wrong loop order can leave the 1→0 result at seven rather than the true five.

### The code

```python
INF = float('inf')

def floyd_warshall(n, edges):
    d = [[INF] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
        nxt[i][i] = i
    for u, v, w in edges:
        if w < d[u][v]:
            d[u][v] = w
            # The first hop of a direct edge
            # is v.
            nxt[u][v] = v
    for k in range(n):
        for i in range(n):
            if d[i][k] == INF:
                continue
            for j in range(n):
                nd = d[i][k] + d[k][j]
                if nd < d[i][j]:
                    d[i][j] = nd
                    # Reuse the first hop of
                    # the improved path.
                    nxt[i][j] = nxt[i][k]
    return d, nxt
```

A single matrix updated in place is safe: during round k, row k and column k do not change, because going through k to reach k adds nothing. So it does not matter whether a later update reads an old or a new value from that row or column.

```formula reference
d[i][k] + d[k][k] = d[i][k] + 0 = d[i][k]
where
i: any start vertex
k: the vertex unlocked this round
d[i][k]: the current best distance from i to k
d[k][k]: the distance from k to itself, 0 when there are no negative cycles
In words: the row and column of the vertex being unlocked cannot improve during its own round, so reading their old or new values gives the same answer.
```

- **Time:** O(m + n³), including edge initialisation, for n vertices and m edges; O(n³) for simple graphs. Skipping rows i that have no route to k can reduce actual iterations.
- **Space:** O(n²).
- **Negative edges:** fine. **Negative cycles:** afterwards some `d[i][i] < 0`.

> [!warning] k must be the outermost loop
> The DP is over k. If you write `for i: for j: for k:`, then d[i][j] is finalised before the entries it depends on are ready. The code still runs and still looks plausible, but gives wrong answers on some graphs.

## Key takeaways
- Keep the intermediate vertex loop outermost.
- The diagonal identifies negative cycles after relaxation.
- In-place updates preserve the recurrence when shortest distances are finite.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
