---
id: graph-dsu-cost-kruskal
title: Amortised Union-Find costs and complete Kruskal
level: intermediate
minutes: 4
sourceLesson: graph-mst
summary: Inverse-Ackermann amortised cost is not a four-instruction per-call promise.
---

The DSU class from the previous unit provides find and union with rank and path compression. Kruskal’s input tuples are (weight, start, end), with numbered vertices. Here n counts vertices and m counts edges, except in the Union-Find cost card, where m counts operations.

## Kruskal's algorithm

Sort all edges by weight. Walk through them, adding each edge unless it would form a cycle with edges already chosen.

On the example:

| Edge | Weight | Action |
|---|---|---|
| A–C | 1 | add |
| B–C | 2 | add |
| D–E | 2 | add |
| E–F | 3 | add |
| A–B | 4 | skip: A, B joined |
| B–D | 5 | add (5 edges: done) |

Each added edge is the lightest edge crossing the cut between its endpoint's current component and everything else, so the cut property guarantees it is safe.

The only hard part is the cycle test: "are u and v already connected by chosen edges?" Running a BFS each time would cost O(n) per edge, for n vertices. That is what **Union-Find** is for.



### Inverse Ackermann

Initialising n singleton sets costs O(n). With rank and compression together, a long sequence of finds and unions costs, on average, an almost constant amount per operation. The bound involves the inverse Ackermann function α, which grows so slowly that it is at most about 4 for any input that fits in a real computer:

```formula reference
T = O(n + m α(n))
where
n: the number of elements (vertices)
m: the number of find and union operations; in Kruskal, about two finds per edge
α(n): the inverse Ackermann function: a function of n that grows so slowly it stays at most about 4 for any n that fits in a real computer (the exact constant depends on the definition used)
T: the total time for initialisation plus all m operations
O(…): Big O: grows at most this fast, up to a constant factor
In words: after setting up one set per element, each find or union costs a tiny, effectively constant amount on average.
```

So a million operations on a million elements cost on the order of a few million steps in total. Inverse-Ackermann definitions vary by small constants; the function grows extremely slowly. This is an amortised growth bound, not a claim that each call performs at most four instructions. Individual calls can take O(log n).

| Variant | Cost per op |
|---|---|
| Naive | O(n) worst |
| Union by rank only | O(log n) |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

### Kruskal in full

```python
def kruskal(n, edges):  # (w, u, v)
    dsu = DSU(n)
    tree, total = [], 0
    for w, u, v in sorted(edges):
        if dsu.union(u, v):
            # Keep only edges that merge
            # components.
            tree.append((u, v, w))
            total += w
            if len(tree) == n - 1:
                break
    return total, tree
```

**Time:** sorting dominates. Sorting the m edges costs O(m log m); the Union-Find work adds only an almost-constant amount per edge, plus O(n) set-up. In a simple graph m is at most about n², so log m is at most about twice log n, and for connected simple graphs the total is conventionally written O(m log n). With a million edges the sort's growth expression is about twenty million; that is a scale, not an exact comparison count.

## Key takeaways
- Inverse-Ackermann amortised cost is not a four-instruction per-call promise.
- Include initialisation and sorting in the full algorithm cost.
- Disconnected input yields a forest.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 1.5 Union-Find](https://algs4.cs.princeton.edu/15uf/)
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
