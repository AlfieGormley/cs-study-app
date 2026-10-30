---
id: graph-bellman-negative-cycles
title: Bellman–Ford rounds and negative cycles
level: intermediate
minutes: 4
sourceLesson: graph-shortest-paths
summary: At most one fewer round than vertices suffices without a reachable negative cycle.
---

The previous unit’s negative-edge graph is A→B 4, A→C 5, C→B −3 and B→D 2. From A, correct distances are A:0, B:2, C:5 and D:4. Here n counts vertices and m counts directed edges; the edge list has numbered endpoints for the implementation below.

## Bellman–Ford

Relax **every edge** for at most one fewer rounds than there are vertices.

```python
def bellman_ford(n, edges, s):
    INF = float('inf')
    dist = [INF] * n
    dist[s] = 0
    for _ in range(n - 1):
        # Track whether another round is
        # needed.
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break  # converged early
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            # A reachable negative cycle can
            # improve.
            return None  # negative cycle
    return dist
```

Why at most one fewer round than vertices? A shortest path without cycles visits each vertex at most once, so it has at most one edge fewer than there are vertices. After the first round, every shortest path that uses one edge is correct; after the second, every one that uses at most two edges; and so on. So on the four-vertex example every distance is final after three rounds, and often sooner: in-place updates can carry an improvement along several edges within one round, which is why the code stops early when a round changes nothing.

> [!analogy] Real-world analogy: news passed along a row of desks
> In a classroom row, each round every pupil may pass what they have heard to the next desk. However the pupils happen to sit, news from one end needs at most one round fewer than the number of desks to reach the other end.
>
> **How it maps:** desks are vertices, passing a note is relaxing an edge, and a round is one pass over the whole edge list. The longest chain the news can need is a cycle-free path, which is why the number of rounds is capped at one fewer than the number of vertices.
>
> **Where it stops:** in class each pupil passes the note once per round. Bellman–Ford relaxes edges in list order and updates distances immediately, so with a lucky edge order one round can carry news down the whole row; the cap is a worst case, not the usual count.

On the negative-edge example above, Bellman–Ford correctly returns A 0, B 2, C 5, D 4.

If an n-th round can still improve something, a **negative cycle** is reachable from the source. Distances are unbounded below for vertices reachable from that cycle; other vertices can still have finite distances. This implementation returns None for the entire result when it detects one. Bellman–Ford detects this; Dijkstra cannot.

- **Time:** up to n − 1 rounds, each relaxing all m edges, so O(nm) when there is at least one edge (plus O(n) to set up the distances). With 100,000 vertices and a million edges that is up to 10¹¹ relaxation attempts: far slower than Dijkstra, which is why you use Bellman–Ford only when you need negative edges or cycle detection.
- **Real uses:** distance-vector routing protocols such as RIP are a distributed Bellman–Ford, each router relaxing the routes its neighbours advertise. Currency arbitrage detection turns exchange rates into weights with a logarithm, which turns multiplying rates into adding weights: a cycle of exchanges that ends with more money than it started with becomes a negative cycle.

```formula reference
w = −log(r)
r_1 r_2 r_3 > 1
w_1 + w_2 + w_3 < 0
where
r: an exchange rate, units of the target currency per unit of the source
w: the edge weight given to that exchange
r_1, r_2, r_3: the rates on the three exchanges of a cycle that returns to the starting currency
w_1, w_2, w_3: their weights
log: logarithm with any fixed base greater than one; numerical exchange-rate quotes use their stated currency units
In words: a cycle of exchanges that ends with more money than it started with has weights summing below zero, a negative cycle.
```

  For example, rates 0.9, 0.9 and 1.25 multiply to 1.0125, a 1.25% profit, so their weights sum to a negative number and Bellman–Ford flags the cycle.

> [!note] SPFA
> The "Shortest Path Faster Algorithm" only re-relaxes edges out of vertices whose distance just changed, using a queue. Its performance depends on edge order and graph structure; its worst-case bound remains O(nm) (vertices times edges) when m ≥ 1.

## Key takeaways
- At most one fewer round than vertices suffices without a reachable negative cycle.
- The extra relaxation test detects cycles reachable from the source.
- In-place relaxation can propagate through several edges in one round.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Bellman–Ford algorithm — Wikipedia](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm)
