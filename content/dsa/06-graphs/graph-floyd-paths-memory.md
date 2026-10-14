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

This is a simplified shortest-path next-hop table. Real forwarding tables can aggregate destinations into network prefixes, use policy and offer multiple next hops.

### Why people like it

Floyd–Warshall is four lines of logic, handles negative weights, has no min-heap, and array-based implementations can exploit contiguous rows and vectorised inner loops. The Python list implementation here does not itself guarantee those optimisations. For n up to a few hundred it is often the simplest correct choice. The three nested loops make the cost easy to count:

```formula
I = n^3
I = 500^3 = 1.25 × 10^8
where
n: the number of vertices; 500 in the example
I: the full triple-loop iteration count before the shown code’s unreachable-row skipping (one per choice of k, i and j)
In words: three nested loops over n vertices run n × n × n times; doubling n multiplies the work by 8.
```

> [!note] Content gap
> CPython, C and NumPy runtime estimates are omitted because the project has no reproducible benchmark with specified hardware, data and implementation.

## Pitfalls

- **Wrong loop order** in Floyd–Warshall: k must be outermost.
- **INF + INF overflow** in C, Java or Go when INF is `INT_MAX`. Skip addition if either operand is the infinity sentinel, and establish bounds that keep every finite sum representable. A large infinity sentinel alone does not prevent overflow or spurious finite paths from adding a negative value to infinity.
- **Memory.** The table grows with the square of the vertex count:

```formula
M = n^2 b
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
- A next-hop table reconstructs only valid unaffected shortest paths.
- An explicit all-pairs table has quadratic storage.
- Infinity sentinel addition and negative cycles need handling beyond the basic recurrence.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/44sp/)
- [Floyd–Warshall — cp-algorithms](https://cp-algorithms.com/graph/all-pair-shortest-path-floyd-warshall.html)
- [Floyd–Warshall algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
