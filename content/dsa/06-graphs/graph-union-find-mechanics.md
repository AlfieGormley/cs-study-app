---
id: graph-union-find-mechanics
title: Union-Find ranks and path compression
level: intermediate
minutes: 3
sourceLesson: graph-mst
summary: Find returns a set representative; successful union merges sets.
---

The previous unit introduced Kruskal: process edges in increasing weight and reject an edge whose endpoints already belong to the same component. Here n is the number of elements. This unit implements that component test.

## Union-Find (disjoint set union)

Union-Find maintains a partition of the vertices into disjoint sets, with two operations:

- `find(x)`: which set is x in? (Returns the set representative, the set's root.)
- `union(a, b)`: merge the sets containing a and b.

Each set is a tree of parent pointers; the root represents the set.

```
parent: 0  1  2  3  4  5
        0  0  1  3  3  4

  0        3
  |        |
  1        4
  |        |
  2        5
```

`find(2)` follows 2 → 1 → 0. `union(2, 5)` links root 3 under root 0 (or vice versa).

Done naively, these trees can degenerate into long chains and `find` becomes O(n). Two tricks fix that.

### Union by rank

Attach the **lower-rank** root under the higher-rank root. After path compression, rank need not equal the current height. Each root keeps a `rank`, an upper bound on its tree's height. A rank only goes up when two trees of equal rank are joined, which at least doubles the smaller size:

```formula
2^r ≤ s ≤ n
r ≤ log_2(n)
r ≤ log_2(10^6) ≈ 19.93
r ≤ 19
where
r: the rank of a root (an upper bound on its tree's height)
s: the number of vertices in that tree
n: the total number of elements; 10^6 in the example
log_2: the base-2 logarithm: how many times you can halve n before reaching 1
≤: is at most
≈: approximately equal to
In words: a tree of rank r has at least 2 to the power r vertices, so with a million elements the integer rank is at most 19.
```

So heights stay O(log n) even without the second trick.

### Path compression

During `find`, point every vertex on the path straight at the root. Until later unions change the root, a subsequent `find` from one of those non-root vertices follows one parent link.

```
before find(2)     after
  0                  0
  |                 / \
  1                1   2
  |
  2
```

### The code

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.parent[x] = root  # flatten
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already joined
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        # Merge roots, not arbitrary
        # elements.
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            # Equal ranks increase the
            # height bound.
            self.rank[ra] += 1
        return True
```

Union by rank keeps recursion depth O(log n), much smaller than a naive chain; it must still fit the runtime’s configured recursion limit.

Ordinary DSU supports incremental undirected connectivity: start with one component per vertex and reduce the count after every successful union. It cannot split a component after deletion. It also ignores direction, so it is not a directed-cycle detector.

## Key takeaways
- Find returns a set representative; successful union merges sets.
- Rank is an upper height bound after compression, not the current height.
- Ordinary Union-Find merges and does not support arbitrary deletion.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/15uf/)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
