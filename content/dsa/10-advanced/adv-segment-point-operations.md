---
id: adv-segment-point-operations
title: Building, querying and updating segment trees
level: advanced
minutes: 4
summary: Disjoint, covered and partial overlap are the three query cases.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Query, update and build

The examples require non-empty arrays and valid inclusive ranges or point indices:

```formula
0 ≤ l ≤ r < n
0 ≤ i < n
where
l: the first index of the query range
r: the last index of the query range (inclusive)
i: the index of a single element to update
n: the number of elements in the array
≤: is at most
<: is less than
In words: ranges and positions must lie inside the array, and a range must not end before it starts.
```

For an 8-element array, `query(2, 5)` is valid and `query(5, 2)` or `update(8, x)` is not. Complexity assumes constant-size summaries and constant-time combines on word-sized values. Integer sums are associative; floating-point sums need numerical-error considerations.

```python
class SegTree:
    def __init__(self, a):
        self.n = len(a)
        if not self.n:
            raise ValueError("empty array")
        self.t = [0] * (4 * self.n)
        self._build(a, 1, 0, self.n - 1)

    def _pull(self, v):
        t = self.t
        # Restore this parent from child
        # sums.
        t[v] = t[2*v] + t[2*v + 1]

    def _build(self, a, v, lo, hi):
        # A leaf represents one array
        # element.
        if lo == hi:
            self.t[v] = a[lo]
            return
        m = (lo + hi) // 2
        self._build(a, 2*v, lo, m)
        self._build(a, 2*v + 1, m + 1, hi)
        # Recompute after either child
        # changes.
        self._pull(v)

    def query(self, l, r):  # inclusive
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:     # disjoint
            return 0
        if l <= lo and hi <= r:  # covered
            # A covered node already has the
            # answer.
            return self.t[v]
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))

    def update(self, i, x):
        self._u(1, 0, self.n-1, i, x)

    def _u(self, v, lo, hi, i, x):
        # A leaf represents one array
        # element.
        if lo == hi:
            self.t[v] = x
            return
        m = (lo + hi) // 2
        if i <= m:
            self._u(2*v, lo, m, i, x)
        else:
            self._u(2*v+1, m+1, hi, i, x)
        # Recompute after either child
        # changes.
        self._pull(v)
```

The query has three cases at each node:

1. **Disjoint**: the node's range misses `[l, r]` entirely. Return the identity (0 for sum, +infinity for min).
2. Covered: the node's range lies inside `[l, r]`. Return its stored value without going deeper.
3. Partial overlap: recurse into both children and combine.

The update walks one root-to-leaf path, then recomputes each node on the way back up.

### Why O(log n)?

- Build: every node (twice the element count, minus one) is computed once: O(n).
- **Update**: one root-to-leaf path, O(1) work per node: O(log n).
- **Query**: at each level, at most two nodes are *partially* overlapped (the ones containing the ends of `[l, r]`). Everything between them is fully covered and stops immediately. So at most four nodes are visited per level.

Counting levels gives the bounds:

```formula
N_build = 2n − 1
N_update ≤ ⌈log_2(n)⌉ + 1
N_query ≤ 4(⌈log_2(n)⌉ + 1)
n = 10^6:  N_update ≤ 21,  N_query ≤ 84
where
n: the number of elements in the array
N_build: the number of nodes the build computes
N_update: the number of nodes a point update touches (one per level, root to leaf; a leaf one level higher than the deepest saves one)
N_query: the number of nodes a range query visits
log_2(n): the base-2 logarithm of n
⌈ ⌉: ceiling: round up to the nearest whole number
≤: is at most
In words: a build touches every node once, an update touches one node per level, and a query touches at most four nodes per level.
```

For a million elements that is at most 21 nodes per update and at most 84 per query, which is why both are O(log n). The bounds assume combining two summaries takes constant time.

## Key takeaways

- Disjoint, covered and partial overlap are the three query cases.
- Point updates recompute summaries on one root-to-leaf path.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
