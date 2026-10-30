---
id: graph-floyd-paths-memory
title: Floyd–Warshall traces, paths and memory
level: intermediate
minutes: 4
sourceLesson: graph-all-pairs
summary: A next-hop table reconstructs only valid unaffected shortest paths.
---

The previous unit’s floyd_warshall(n, edges) returns distance and next-hop matrices. Here n counts vertices and m counts edges. Each outer round permits one more intermediate vertex, and row/column indexing uses numbered vertices.

### A worked example

```
edges:  0->1 3   0->3 7   1->0 8
        1->2 2   2->0 5   2->3 1
        3->0 2
```

| k | Key improvements |
|---|---|
| via 0 | 2→1: eight; 3→1: five; 1→3: fifteen |
| via 1 | 0→2: five; 3→2: seven |
| via 2 | 0→3: six; 1→0: seven; 1→3: three |
| via 3 | 1→0: five; 2→0: three; 2→1: six |

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

> [!analogy] Real-world analogy: signposts at every junction
> Imagine every junction in a town had a signpost listing every destination with an arrow for the road to take next. To get anywhere you never need the whole route: you follow the arrow at each junction you reach.
>
> **How it maps:** the signpost at junction i, arrow for destination j, is `nxt[i][j]`. Following arrows junction by junction is the loop in `path`, which keeps reading `nxt[current][j]` until it arrives.
>
> **Where it stops:** real signposts may be missing or inconsistent. The table only works if every arrow agrees with the same set of shortest routes, which holds after Floyd–Warshall when no negative cycle affects the pair; otherwise the arrows can lead round in circles, which is what the guard in `path` catches.

This is a simplified shortest-path next-hop table. Real forwarding tables can aggregate destinations into network prefixes, use policy and offer multiple next hops.

### Why people like it

Floyd–Warshall is four lines of logic, handles negative weights, has no min-heap, and array-based implementations can exploit contiguous rows and vectorised inner loops. The Python list implementation here does not itself guarantee those optimisations. For n up to a few hundred it is often the simplest correct choice. The three nested loops make the cost easy to predict: n × n × n inner steps, 125 million for 500 vertices, and doubling n multiplies the work by 8.

## Pitfalls

- **Wrong loop order** in Floyd–Warshall: k must be outermost.
- **INF + INF overflow** in C, Java or Go when INF is `INT_MAX`. Skip addition if either operand is the infinity sentinel, and establish bounds that keep every finite total representable. A large infinity sentinel alone does not prevent overflow or spurious finite paths from adding a negative value to infinity.
- **Memory.** The table grows with the square of the vertex count. For 100,000 vertices it has 10¹⁰ entries: about 40 GB (decimal gigabytes) at 4 bytes each, before any next-hop table. Full APSP tables are for small graphs.

- **Negative cycles** make some distances undefined (−∞). Check the diagonal and propagate: any pair whose path can touch a negative cycle is −∞.

## Key takeaways
- A next-hop table reconstructs only valid unaffected shortest paths.
- An explicit all-pairs table has quadratic storage.
- Infinity sentinel addition and negative cycles need handling beyond the basic recurrence.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.4 Shortest paths](https://algs4.cs.princeton.edu/44sp/)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
