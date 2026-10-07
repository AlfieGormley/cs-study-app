---
id: graph-all-pairs
title: All-pairs shortest paths
level: intermediate
minutes: 11
summary: Floyd–Warshall as dynamic programming over intermediate vertices, transitive closure with bitsets, and when running Dijkstra (or Johnson's algorithm) n times is the better choice.
---

Sometimes one source is not enough. A delivery company wants the driving time between every pair of its 300 depots. A network tool wants every router's distance to every other to find the network's **diameter**. A game precomputes distances between all waypoints so that AI agents can look them up instantly.

That is the **all-pairs shortest paths (APSP)** problem: fill an n × n table where `d[i][j]` is the shortest distance from i to j. Materialising this explicit table requires Ω(n²) output work; a compressed or query-only representation is a different task. Assume finite weights and constant-time arithmetic in the complexity bounds below.

## Floyd–Warshall

Floyd–Warshall is a short, elegant piece of **dynamic programming**.

### The idea

Number the vertices 0 to n − 1. Define:

> dₖ[i][j] = the shortest i→j distance using only vertices 0, ..., k − 1 as **intermediate** stops.

- d₀ allows no intermediates: use minimum direct edge weights, also allowing the zero-length diagonal walk (so a negative self-loop can make the diagonal negative), and ∞ for absent connections.
- dₙ allows every vertex: it is the answer.

For the finite shortest-distance recurrence, assume no negative cycles. Going from k to k + 1, we unlock vertex k. A shortest path using intermediates from {0..k} either avoids k (cost dₖ[i][j]) or passes through k exactly once (cost dₖ[i][k] + dₖ[k][j]). So:

```
d[i][j] = min(d[i][j],
              d[i][k] + d[k][j])
```

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
            nxt[u][v] = v
    for k in range(n):
        for i in range(n):
            if d[i][k] == INF:
                continue
            for j in range(n):
                nd = d[i][k] + d[k][j]
                if nd < d[i][j]:
                    d[i][j] = nd
                    nxt[i][j] = nxt[i][k]
    return d, nxt
```

A single matrix updated in place is safe: during round k, row k and column k do not change (d[i][k] + d[k][k] = d[i][k] when there are no negative cycles), so it does not matter whether you read old or new values.

- **Time:** O(m + n³), including edge initialisation; O(n³) for simple graphs. The unreachable-row shortcut can reduce actual iterations.
- **Space:** O(n²).
- **Negative edges:** fine. **Negative cycles:** afterwards some `d[i][i] < 0`.

> [!warning] k must be the outermost loop
> The DP is over k. If you write `for i: for j: for k:`, then d[i][j] is finalised before the entries it depends on are ready. The code still runs and still looks plausible, but gives wrong answers on some graphs.

### A worked example

```
edges:  0->1 3   0->3 7   1->0 8
        1->2 2   2->0 5   2->3 1
        3->0 2
```

| k | Key improvements |
|---|---|
| via 0 | 2→1 = 5+3 = 8, 3→1 = 2+3 = 5, 1→3 = 8+7 = 15 |
| via 1 | 0→2 = 3+2 = 5, 3→2 = 5+2 = 7 |
| via 2 | 0→3 = 5+1 = 6, 1→0 = 2+5 = 7, 1→3 = 2+1 = 3 |
| via 3 | 1→0 = 3+2 = 5, 2→0 = 1+2 = 3, 2→1 = 3+3 = 6 |

Final matrix:

```
      0   1   2   3
 0 [  0   3   5   6 ]
 1 [  5   0   2   3 ]
 2 [  3   6   0   1 ]
 3 [  2   5   7   0 ]
```

Notice 1→0 improves twice: 8 directly, then 7 via 2, then 5 via 2 and 3 (1→2→3→0).

### Reconstructing paths

Only reconstruct a pair after confirming no negative cycle lies on a route between its endpoints; affected pairs have no shortest path. For valid unaffected pairs, `nxt` stores the first hop. The guard below catches a cyclic or malformed table, but is not itself a complete negative-cycle test:

```python
def path(nxt, i, j):
    if nxt[i][j] is None:
        return None
    p, seen = [i], {i}
    while i != j:
        i = nxt[i][j]
        if i is None or i in seen:
            raise ValueError("bad path")
        seen.add(i)
        p.append(i)
    return p

# path(nxt, 1, 0) -> [1, 2, 3, 0]
```

This is a simplified shortest-path next-hop table. Real forwarding tables can aggregate destinations into prefixes, use policy and offer multiple next hops.

### Why people like it

Floyd–Warshall is four lines of logic, handles negative weights, has no heap, and array-based implementations can exploit contiguous rows and vectorised inner loops. The Python list implementation here does not itself guarantee those optimisations. For n up to a few hundred it is often the simplest correct choice. A full n = 500 triple loop has 1.25 × 10⁸ inner iterations.

> [!note] Content gap
> CPython, C and NumPy runtime estimates are omitted because the project has no reproducible benchmark with specified hardware, data and implementation.

## Transitive closure

Sometimes you only care whether j is **reachable** from i. Replace min/+ with OR/AND (Warshall's algorithm):

```
reach[i][j] = reach[i][j] or
    (reach[i][k] and reach[k][j])
```

Pack each row into a bitset, and a whole row updates in one operation: "if i reaches k, then i reaches everything k reaches". Python's arbitrary-size integers make this easy:

```python
def closure(n, edges):
    reach = [1 << i for i in range(n)]
    for u, v in edges:
        reach[u] |= 1 << v
    for k in range(n):
        bit = 1 << k
        for i in range(n):
            if reach[i] & bit:
                reach[i] |= reach[k]
    return reach
```

This computes reflexive transitive closure: every vertex reaches itself via a zero-length walk. With packed w-bit words, a row OR takes O(⌈n/w⌉) word operations, not constant time. Including loop and input costs gives O(m + n²⌈n/w⌉). Python integers use implementation-specific internal digits (`sys.int_info.bits_per_digit`), not necessarily 64-bit payloads. Uses: "can this permission/role reach that resource?", "does module A transitively depend on B?", and query optimisers deriving implied joins.

For sparse graphs, a BFS from every vertex costs O(n(n + m)), which beats n³ when m is small. On a DAG you can compute closures in reverse topological order by OR-ing successors' bitsets.

## When to run Dijkstra n times instead

APSP with non-negative weights can also be done by running single-source Dijkstra from every vertex.

| Method | Time |
|---|---|
| Floyd–Warshall | O(n³) |
| n × Dijkstra (heap) | O(n (n + m) log n) |
| n × BFS (unweighted) | O(n (n + m)) |
| Johnson's, binary heaps | O(n(n + m) log(n + 1)) |

On a **sparse** graph, m ≈ cn, so n × Dijkstra is about O(n² log n), much better than n³.

> [!example] A road network
> n = 10,000, m = 40,000.
> - Floyd–Warshall: n³ = 10¹² steps.
> - n × Dijkstra: 10⁴ × 5 × 10⁴ × log₂ 10⁴ (≈ 13) ≈ 6.5 × 10⁹.
>
> The ratio of these growth expressions is roughly 150; it is not a measured speedup or a count of equivalent machine instructions. On a dense graph (m ≈ n²) the heap version becomes O(n³ log n), worse than Floyd–Warshall.

You also often do not need *all* pairs. If you only need distances between 300 depots in a 10-million-node road graph, run 300 Dijkstras (or a bidirectional/contraction-hierarchy query per pair) rather than any all-pairs algorithm over the whole road graph.

## Johnson's algorithm: negative edges on sparse graphs

Dijkstra cannot handle negative edges, and Floyd–Warshall is O(n³). Johnson's algorithm gets the best of both:

1. Add a new vertex q with a 0-weight edge to every vertex.
2. Run **Bellman–Ford** from q to get h(v) for each v (O(n(n + m)) for the augmented graph). If it finds a negative cycle, stop.
3. **Reweight** each edge: w'(u, v) = w(u, v) + h(u) − h(v). Because h(v) ≤ h(u) + w(u, v) (it is a shortest-path distance), every w' ≥ 0.
4. Run **Dijkstra** from every vertex on w'.
5. Undo the shift: d(u, v) = d'(u, v) − h(u) + h(v).

Why step 3 preserves shortest paths: along any path u → ... → v, the h terms telescope, so every u→v path changes by exactly h(u) − h(v). The ranking of paths is unchanged. (Compare adding a constant to every edge, which penalises long paths more and breaks the ranking.)

With binary heaps on simple graphs, total time is O(n(n + m) log(n + 1)), including the augmented Bellman–Ford run. When m = Ω(n), this is commonly simplified to O(nm log n).

## Pitfalls

- **Wrong loop order** in Floyd–Warshall: k must be outermost.
- **INF + INF overflow** in C, Java or Go when INF is `INT_MAX`. Skip addition if either operand is the infinity sentinel, and establish bounds that keep every finite sum representable. A large sentinel alone does not prevent overflow or spurious finite paths from adding a negative value to infinity.
- **Memory.** n = 100,000 means 10¹⁰ entries; at 4 bytes each that is 40 GB. APSP tables are for small n.
- **Negative cycles** make some distances undefined (−∞). Check the diagonal and propagate: any pair whose path can touch a negative cycle is −∞.

## Key takeaways
- APSP outputs n² distances. Floyd–Warshall computes them by DP over allowed intermediate vertices in O(n³) time and O(n²) space.
- The k loop must be outermost. Negative edges are fine; a negative d[i][i] reveals a negative cycle.
- Transitive closure is Floyd–Warshall with OR/AND, and bitset rows divide the work by the word size.
- On sparse graphs with non-negative weights, n × Dijkstra (O(n(n + m) log n)) beats O(n³).
- Johnson's algorithm reweights with Bellman–Ford potentials so n Dijkstras can handle negative edges.

## Further reading
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
- [Johnson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Johnson%27s_algorithm)
- [Transitive closure — Wikipedia](https://en.wikipedia.org/wiki/Transitive_closure)
- [Shortest paths — NetworkX docs](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
