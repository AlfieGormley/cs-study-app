---
id: graph-all-pairs
title: All-pairs shortest paths
level: intermediate
minutes: 11
summary: Floyd–Warshall as dynamic programming over intermediate vertices, transitive closure with bitsets, and when running Dijkstra (or Johnson's algorithm) n times is the better choice.
---

Sometimes one source is not enough. A delivery company wants the driving time between every pair of its 300 depots. A network tool wants every router's distance to every other to find the network's **graph diameter** (the longest shortest path). A game precomputes distances between all waypoints so that AI agents can look them up instantly.

That is the **all-pairs shortest paths (APSP)** problem: fill an n × n table where `d[i][j]` is the shortest distance from i to j. Just writing the answer down takes a lot of work:

```formula
N = n × n = n^2
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

- d₀ allows no intermediates: use minimum direct edge weights, also allowing the zero-length diagonal walk (so a negative graph self-loop can make the diagonal negative), and ∞ for absent connections.
- dₙ allows every vertex: it is the answer.

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

The worked line is from the example below: before any vertex is unlocked, 2 cannot reach 1, but via vertex 0 it costs 5 + 3 = 8. The code drops the k subscript and updates one table in place.

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

A single matrix updated in place is safe: during round k, row k and column k do not change, because going through k to reach k adds nothing:

```formula
d[i][k] + d[k][k] = d[i][k] + 0 = d[i][k]
where
i: any start vertex
k: the vertex unlocked this round
d[i][k]: the current best distance from i to k
d[k][k]: the distance from k to itself, 0 when there are no negative cycles
In words: the entries in row k and column k can't improve in round k, so reading old or new values gives the same answer.
```

So it does not matter whether you read old or new values.

- **Time:** O(m + n³), including edge initialisation, for n vertices and m edges; O(n³) for simple graphs. Skipping rows i that have no route to k can reduce actual iterations.
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
| via 3 | 1→0 = 3+2 = 5, 2→0 = 1+2 = 3, 2→1 = 1+5 = 6 |

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

Floyd–Warshall is four lines of logic, handles negative weights, has no heap, and array-based implementations can exploit contiguous rows and vectorised inner loops. The Python list implementation here does not itself guarantee those optimisations. For n up to a few hundred it is often the simplest correct choice. The three nested loops make the cost easy to count:

```formula
I = n^3
I = 500^3 = 1.25 × 10^8
where
n: the number of vertices; 500 in the example
I: the number of inner-loop iterations (one per choice of k, i and j)
In words: three nested loops over n vertices run n × n × n times; doubling n multiplies the work by 8.
```

> [!note] Content gap
> CPython, C and NumPy runtime estimates are omitted because the project has no reproducible benchmark with specified hardware, data and implementation.

## Transitive closure

Sometimes you only care whether j is **reachable** from i. Replace min/+ with OR/AND (Warshall's algorithm):

```formula
R[i][j] ← R[i][j] ∨ (R[i][k] ∧ R[k][j])
R[2][1] ← 0 ∨ (1 ∧ 1) = 1
where
i, j: the start and end vertices
k: the vertex unlocked this round
R[i][j]: 1 (true) if j is known to be reachable from i, 0 (false) otherwise
∨: logical OR: true if either side is true
∧: logical AND: true only if both sides are true
←: replace the old value with the new one
In words: i reaches j if it already did, or if i reaches k and k reaches j.
```

In the example graph, 2 has no edge to 1, but 2 reaches 0 and 0 reaches 1, so round k = 0 sets R[2][1] to 1.

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

This computes reflexive transitive closure: every vertex reaches itself via a zero-length walk. A row of n bits is stored in machine words of w bits each, so OR-ing two rows costs one operation per word:

```formula
c_row = ⌈n / w⌉
c_row = ⌈10000 / 64⌉ = 157
T = O(m + n^2 × ⌈n / w⌉)
where
n: the number of vertices, so each row has n bits; 10,000 in the example
w: the word size in bits; 64 on a typical 64-bit CPU
m: the number of edges
c_row: word operations to OR one row into another
⌈ ⌉: ceiling: round up to a whole number
T: the total running time of bitset transitive closure
O(…): Big O: grows at most this fast, up to a constant factor
In words: packing bits divides the inner loop's work by the word size, roughly 64 times less.
```

A row OR is therefore not constant time, but 157 word operations is far fewer than 10,000 single-bit ones. Python integers use implementation-specific internal digits (`sys.int_info.bits_per_digit`), not necessarily 64-bit payloads. Uses: "can this permission/role reach that resource?", "does module A transitively depend on B?", and query optimisers deriving implied joins.

For sparse graphs, a BFS from every vertex costs O(n(n + m)), n traversals of O(n + m) each, which beats n³ when m is small. On a DAG you can compute closures in reverse topological order by OR-ing together the bitsets of the vertices each one has edges to.

## When to run Dijkstra n times instead

APSP with non-negative weights can also be done by running single-source Dijkstra from every vertex.

In the table, n is the number of vertices, m the number of edges and log the base-2 logarithm.

| Method | Time |
|---|---|
| Floyd–Warshall | O(n³) |
| n × Dijkstra (heap) | O(n (n + m) log n) |
| n × BFS (unweighted) | O(n (n + m)) |
| Johnson's, binary heaps | O(n(n + m) log(n + 1)) |

On a **sparse** graph the edge count is a small multiple of the vertex count, and n Dijkstras win:

```formula
m ≈ c × n
n × (n + m) × log(n)
  ≈ (1 + c) × n^2 × log(n)
where
n: the number of vertices
m: the number of edges
c: a small constant, the average out-degree; 4 in the example below
log(n): the logarithm of n, base 2
≈: approximately equal to
In words: on a sparse graph n Dijkstras cost about n² log n, which grows much more slowly than Floyd–Warshall's n³.
```

For a road network with n = 10,000 and m = 40,000:

```formula
T_FW = n^3 = (10^4)^3 = 10^12
T_D = n × (n + m) × log_2(n)
T_D ≈ 10^4 × 5 × 10^4 × 13
T_D ≈ 6.5 × 10^9
where
n: the number of vertices; 10^4
m: the number of edges; 4 × 10^4
log_2(n): the base-2 logarithm; log_2(10^4) ≈ 13.3
T_FW: Floyd–Warshall's growth expression
T_D: the growth expression for n runs of heap Dijkstra
≈: approximately equal to
In words: Floyd–Warshall's expression is about 150 times larger here.
```

The ratio of these growth expressions is roughly 150; it is not a measured speedup or a count of equivalent machine instructions. On a dense graph (m close to n²) the heap version becomes O(n³ log n), worse than Floyd–Warshall.

You also often do not need *all* pairs. If you only need distances between 300 depots in a 10-million-node road graph, run 300 Dijkstras (or a bidirectional/contraction-hierarchy query per pair) rather than any all-pairs algorithm over the whole road graph.

## Johnson's algorithm: negative edges on sparse graphs

Dijkstra cannot handle negative edges, and Floyd–Warshall is O(n³). Johnson's algorithm gets the best of both:

1. Add a new vertex q with a 0-weight edge to every vertex.
2. Run **Bellman–Ford** from q to get h(v) for each v (O(n(n + m)) for the augmented graph). If it finds a negative cycle, stop.
3. **Reweight** each edge by adding the potential of its start and subtracting the potential of its end (formula below). Because the potentials are shortest-path distances, every new weight is non-negative.
4. Run **Dijkstra** from every vertex on w'.
5. Undo the shift on each answer.

Steps 3 and 5 in full:

```formula
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

For example, with h(u) = 0, h(v) = −3 and an edge u→v of weight −3, the new weight is −3 + 0 − (−3) = 0.

Why step 3 preserves shortest paths: along any path u → x₁ → … → v, each middle potential is added once and subtracted once, so the h terms telescope (cancel in pairs) and every u→v path changes by exactly h(u) − h(v). The ranking of paths is unchanged. (Compare adding a constant to every edge, which penalises long paths more and breaks the ranking.)

With binary heaps on simple graphs, total time is O(n(n + m) log(n + 1)), including the augmented Bellman–Ford run. When m grows at least as fast as n (written m = Ω(n), Big Omega meaning "at least this fast"), this is commonly simplified to O(nm log n).

## Pitfalls

- **Wrong loop order** in Floyd–Warshall: k must be outermost.
- **INF + INF overflow** in C, Java or Go when INF is `INT_MAX`. Skip addition if either operand is the infinity sentinel, and establish bounds that keep every finite sum representable. A large sentinel alone does not prevent overflow or spurious finite paths from adding a negative value to infinity.
- **Memory.** The table grows with the square of the vertex count:

```formula
M = n^2 × b
M = (10^5)^2 × 4 B = 4 × 10^10 B = 40 GB
where
M: the memory for the full distance table
n: the number of vertices; 100,000
b: bytes per entry; 4 for a 32-bit integer
B: byte, 8 bits
GB: gigabyte, 10^9 bytes
In words: 10¹⁰ entries at 4 bytes each is 40 GB, so APSP tables are for small n.
```

- **Negative cycles** make some distances undefined (−∞). Check the diagonal and propagate: any pair whose path can touch a negative cycle is −∞.

## Key takeaways
- APSP outputs n² distances for n vertices. Floyd–Warshall computes them by DP over allowed intermediate vertices in O(n³) time and O(n²) space.
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
