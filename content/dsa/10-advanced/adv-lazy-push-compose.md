---
id: adv-lazy-push-compose
title: Pushing and composing lazy updates
level: advanced
minutes: 4
summary: Push pending updates before descending into children, including during queries.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Implementing deferred updates

The following complete sum-tree example starts from zeros and uses valid inclusive ranges. Its pending tag has the meaning introduced in the previous unit.

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
            # Children now own the deferred
            # addition.
            self.lz[v] = 0

    def add(self, l, r, x):
        self._add(1, 0, self.n-1, l, r, x)

    def _add(self, v, lo, hi, l, r, x):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            self._apply(v, lo, hi, x)
            return
        # Make child summaries current
        # first.
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        self._add(2*v, lo, m, l, r, x)
        self._add(2*v+1, m+1, hi, l, r, x)
        t = self.t
        # Restore this parent from child
        # sums.
        t[v] = t[2*v] + t[2*v + 1]

    def query(self, l, r):
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            # A covered node already has the
            # answer.
            return self.t[v]
        # Make child summaries current
        # first.
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))
```

> [!example] Tracing a lazy update
> On 8 zeros, `add(0, 3, 5)` reaches node `[0,3]`, which is fully covered. It sets that node's sum to 20 and its tag to 5, and the root's sum to 20. The four leaves are not touched at all. A later `add(2, 5, 1)` must go inside `[0,3]`, so it first pushes the tag: `[0,1]` and `[2,3]` each get sum 10 and tag 5.

Both operations now visit O(log n) nodes, so range update and range query are both **O(log n)**.

Lazy propagation needs two properties:

- You can update a node's summary without looking at its children.
- Pending tags **compose**: two adds become one add. Mixing "assign" and "add" works too, but the tag must record the order (an assignment wipes out earlier adds).

For a range add, both properties are one line each:

```formula
S_new = S_old + xw
M_new = M_old + x
z_2 = (z_0 + x_1) + x_2 = z_0 + (x_1 + x_2)
where
S_old, S_new: a node's stored sum before and after the add
M_old, M_new: a node's stored minimum before and after the add
w: the width of the node: the number of elements it covers
x: the amount added to every element
z_0: the node's pending tag before two later adds
z_2: the node's pending tag after both adds
x_1, x_2: two adds applied one after the other
In words: a sum grows by x for every element and a minimum grows by exactly x, and two pending adds merge into a single add of their total.
```

So a node covering 4 elements with sum 20 and minimum 3 becomes sum 28 and minimum 5 after adding 2.

Some updates fail the first test. "Replace each range element with its remainder after division by a positive integer" changes a sum in a way that depends on every element, so plain lazy propagation cannot do it.

## Key takeaways

- Push pending updates before descending into children, including during queries.
- Tag composition must preserve update order when assignments and additions mix.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
