---
id: graph-union-find-mechanics
title: Union-Find ranks and path compression
level: intermediate
minutes: 3
sourceLesson: graph-mst
summary: Find returns a set representative; successful union merges sets.
---

Kruskal's algorithm, in the next unit, processes edges in increasing weight and rejects an edge whose endpoints already belong to the same component. Here n is the number of elements. This unit builds the structure that answers that component test quickly.

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

Done naively, these trees can degenerate into long chains and `find` becomes O(n): each union might hang one tree under the end of another, and a `find` must then walk the whole chain. Two tricks fix that.

> [!analogy] Real-world analogy: companies merging
> Every employee knows their manager, and following managers upwards ends at a company's chief executive. Two people work for the same company exactly when their chains end at the same chief executive. When two companies merge, one chief executive simply starts reporting to the other.
>
> **How it maps:** employees are elements, "my manager" is the parent pointer, and the chief executive is the root that `find` returns. A merger is `union`: only the two roots change. Putting the company with the shorter chain of command under the one with the longer chain is union by rank, and an employee who, after asking up the chain, starts reporting straight to the chief executive is path compression.
>
> **Where it stops:** real companies can split again and staff can move. Union-Find only ever merges sets; it has no cheap way to split one.

### Union by rank

Attach the **lower-rank** root under the higher-rank root. After path compression, rank need not equal the current height. Each root keeps a `rank`, an upper bound on its tree's height. A rank only goes up when two trees of equal rank are joined, which at least doubles the size of the tree with that rank. So a tree's size at least doubles every time its rank rises, and with a million elements no rank can exceed 19. Heights therefore stay O(log n) even without the second trick.

```formula reference
2^r ≤ s ≤ n
r ≤ log_2(n)
where
r: the rank of a root (an upper bound on its tree's height)
s: the number of elements in that tree
n: the total number of elements
log_2: the base-2 logarithm: how many times you can halve n before reaching 1
≤: is at most
In words: a tree whose root has a given rank holds at least two to the power of that rank elements, so ranks, and therefore heights, grow only logarithmically with the number of elements.
```

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
- Find returns a set representative; a successful union joins two sets.
- Rank is an upper height bound after compression, not the current height.
- Ordinary Union-Find merges and does not support arbitrary deletion.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 1.5 Union-Find](https://algs4.cs.princeton.edu/15uf/)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
