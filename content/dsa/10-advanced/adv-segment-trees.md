---
id: adv-segment-trees
title: Segment trees
level: advanced
minutes: 15
summary: A binary tree of range summaries that answers range queries and applies updates in O(log n), plus lazy propagation for updating whole ranges at once.
---

Suppose you have an array and two kinds of request arriving in any order: "what is the sum (or minimum, or maximum) of `a[l..r]`?" and "change `a[i]`".

- A plain array makes updates O(1) but queries O(n).
- A prefix-sum array makes sum queries O(1) but every update O(n), because every later prefix changes.

On large arrays, many O(n) operations can become expensive. A **segment tree** makes both operations O(log n). It works for any operation that combines associatively, not just sums.

## The idea: store answers for halves, quarters, eighths...

Each node of a segment tree is responsible for a contiguous range of the array and stores the answer for that range. The root covers everything; each node splits its range in half between its two children; the leaves are single elements.

For `a = [5, 2, 8, 1, 9, 3, 7, 4]` with sums:

```
              [0,7]=39
         /              \
    [0,3]=16          [4,7]=23
    /      \          /      \
 [0,1]=7 [2,3]=9  [4,5]=12 [6,7]=11
  / \     / \      / \      / \
 5   2   8   1    9   3    7   4
```

Any range can be assembled from a handful of these precomputed pieces. The sum of `a[2..5]` is just `[2,3] + [4,5] = 9 + 12 = 21`: two nodes instead of four elements. For long ranges the saving is enormous.

## Storing it in an array

Like a binary heap, the tree lives in a flat array. The root is index 1; node `v` has children `2v` and `2v + 1`.

How big must the array be? The tree has height ceil(log2 n), so it needs fewer than 2 × 2^ceil(log2 n) slots. That is always below **4n**, which is why implementations allocate `4 * n`. (When n is a power of two, 2n is enough.)

## Query, update and build

The examples require non-empty arrays and valid inclusive ranges `0 ≤ l ≤ r < n` or point indices `0 ≤ i < n`. Complexity assumes constant-size summaries and constant-time combines on word-sized values. Integer sums are associative; floating-point sums need numerical-error considerations.

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
        t[v] = t[2*v] + t[2*v + 1]

    def _build(self, a, v, lo, hi):
        if lo == hi:
            self.t[v] = a[lo]
            return
        m = (lo + hi) // 2
        self._build(a, 2*v, lo, m)
        self._build(a, 2*v + 1, m + 1, hi)
        self._pull(v)

    def query(self, l, r):  # inclusive
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:     # disjoint
            return 0
        if l <= lo and hi <= r:  # covered
            return self.t[v]
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))

    def update(self, i, x):
        self._u(1, 0, self.n-1, i, x)

    def _u(self, v, lo, hi, i, x):
        if lo == hi:
            self.t[v] = x
            return
        m = (lo + hi) // 2
        if i <= m:
            self._u(2*v, lo, m, i, x)
        else:
            self._u(2*v+1, m+1, hi, i, x)
        self._pull(v)
```

The query has three cases at each node:

1. **Disjoint**: the node's range misses `[l, r]` entirely. Return the identity (0 for sum, +infinity for min).
2. **Covered**: the node's range lies inside `[l, r]`. Return its stored value without going deeper.
3. **Partial overlap**: recurse into both children and combine.

The update walks one root-to-leaf path, then recomputes each node on the way back up.

### Why O(log n)?

- **Build**: each of the roughly 2n nodes is computed once: O(n).
- **Update**: one path of length ceil(log2 n), O(1) work per node: O(log n).
- **Query**: at each level, at most two nodes are *partially* overlapped (the ones containing the ends of `[l, r]`). Everything between them is fully covered and stops immediately. So at most four nodes are visited per level, giving O(log n).

## Beyond sums: what can a node store?

The structure works whenever the combine operation is **associative**: `(x ⊕ y) ⊕ z = x ⊕ (y ⊕ z)`, with an identity for the empty range. Sum, min, max, gcd, bitwise AND/OR/XOR and matrix products all qualify.

Associative is enough; **commutative is not required**. The recursive code always combines the left child before the right, so non-commutative operations like matrix multiplication or string concatenation work, as long as you keep that order. Actual string concatenation is not constant-time, and matrix costs depend on dimension; their runtimes include combine costs.

You can also store a small **struct** per node. The famous example is the **maximum subarray sum** over a range, with point updates. Each node stores four numbers:

| Field | Meaning |
|---|---|
| `sum` | total of the range |
| `pre` | best prefix sum |
| `suf` | best suffix sum |
| `best` | best subarray sum |

Combining left `L` and right `R`:

```
sum  = L.sum + R.sum
pre  = max(L.pre, L.sum + R.pre)
suf  = max(R.suf, R.sum + L.suf)
best = max(L.best, R.best,
           L.suf + R.pre)
```

The best subarray is either entirely in one half or crosses the middle, in which case it is a suffix of the left plus a prefix of the right. Kadane's algorithm cannot handle updates; this can, in O(log n) each.

## Lazy propagation: updating whole ranges

Now add a third request: "add `x` to every element of `a[l..r]`". Doing it as r − l + 1 point updates costs O(n log n) for a big range.

**Lazy propagation** applies a range update the same way a query reads a range: stop at fully covered nodes. At such a node, update its stored sum (`+ x × length`) and leave a **pending tag** saying "my children still owe `+x`". The tag is **pushed down** to the children only when some later operation needs to go below that node.

```python
class LazySeg:
    def __init__(self, n):
        if n < 1:
            raise ValueError("n > 0")
        self.n = n
        self.t = [0] * (4 * n)   # sums
        self.lz = [0] * (4 * n)  # pending

    def _apply(self, v, lo, hi, x):
        # add x to every element under v
        self.t[v] += x * (hi - lo + 1)
        self.lz[v] += x

    def _push(self, v, lo, hi):
        x = self.lz[v]
        if x:
            m = (lo + hi) // 2
            self._apply(2*v, lo, m, x)
            self._apply(2*v+1, m+1, hi, x)
            self.lz[v] = 0

    def add(self, l, r, x):
        self._add(1, 0, self.n-1, l, r, x)

    def _add(self, v, lo, hi, l, r, x):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            self._apply(v, lo, hi, x)
            return
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        self._add(2*v, lo, m, l, r, x)
        self._add(2*v+1, m+1, hi, l, r, x)
        t = self.t
        t[v] = t[2*v] + t[2*v + 1]

    def query(self, l, r):
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            return self.t[v]
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))
```

> [!example] Tracing a lazy update
> On 8 zeros, `add(0, 3, 5)` reaches node `[0,3]`, which is fully covered. It sets that node's sum to 20 and its tag to 5, and the root's sum to 20. The four leaves are not touched at all. A later `add(2, 5, 1)` must go inside `[0,3]`, so it first pushes the tag: `[0,1]` and `[2,3]` each get sum 10 and tag 5.

Both operations now visit O(log n) nodes, so range update and range query are both **O(log n)**.

Lazy propagation needs two properties:

- You can update a node's summary without looking at its children (sum increases by `x × length`; min increases by `x`).
- Pending tags **compose**: two adds become one add. Mixing "assign" and "add" works too, but the tag must record the order (an assignment wipes out earlier adds).

Some updates fail the first test. "Replace every `a[i]` in a range with `a[i] mod k`" changes a sum in a way that depends on every element, so plain lazy propagation cannot do it.

## The iterative bottom-up version

For point updates and commutative operations there is a compact, fast, non-recursive form. Leaves sit at `n .. 2n − 1`, and node `i`'s parent is `i // 2`. It needs only 2n slots.

```python
def build(a):
    n = len(a)
    t = [0] * n + list(a)
    for i in range(n - 1, 0, -1):
        t[i] = t[2*i] + t[2*i + 1]
    return t

def query(t, n, l, r):  # half-open [l, r)
    res = 0
    l, r = l + n, r + n
    while l < r:
        if l & 1:   # l is a right child
            res += t[l]
            l += 1
        if r & 1:   # r - 1 is a left child
            r -= 1
            res += t[r]
        l, r = l // 2, r // 2
    return res
```

It avoids recursive-call overhead.

> [!note] Content gap: performance multiplier
> No fixed speedup is supplied because the original “several times faster” claim lacked a reproducible benchmark for a specified implementation and workload.

## Where segment trees are used

- **Competitive programming and interviews**: range sum/min/max with updates, "count of smaller numbers after self" (after coordinate compression), and booking problems such as "maximum number of overlapping events" (range add plus range max).
- **Computational geometry**: sweep-line algorithms, such as computing the area of a union of rectangles, keep a segment tree over the y-coordinates.
- **Huge index ranges**: a **dynamic** (sparse) segment tree creates nodes only when touched, so it can cover indices up to 10^9 with memory proportional to the operations performed.

> [!note] A name clash
> In computational geometry, "segment tree" traditionally names a related structure that stores a set of *intervals* and answers "which intervals contain point x?" in O(log n + k). The Wikipedia article describes that version. The array-based range-query tree in this lesson is the meaning used in competitive programming and interviews.

## Pitfalls

- **Inclusive vs half-open ranges.** Pick one convention and stick to it; mixing them is the most common bug.
- **Wrong identity.** Returning 0 for a disjoint range in a *min* tree silently corrupts answers. Use +infinity.
- **Forgetting to push.** In a lazy tree, every operation that descends past a node must push its tag first, including queries.
- **Overkill.** If you only need prefix sums with point updates, a Fenwick tree (next lesson) is shorter and often has lower overhead; measure the actual workload. If the array never changes, a prefix-sum array or sparse table is simpler still.

## Key takeaways
- A segment tree stores the answer for every node's range; any query range decomposes into O(log n) nodes.
- Build O(n), point update O(log n), range query O(log n), in a `4n` array.
- Any associative combine works, including non-commutative ones and multi-field nodes such as max subarray sum.
- Lazy propagation defers range updates with tags pushed down on demand, making range update and range query both O(log n).
- Use the identity element for disjoint ranges and push tags before descending.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
