---
id: adv-segment-iterative-tradeoffs
title: Iterative segment trees and practical choices
level: advanced
minutes: 4
summary: A bottom-up tree puts leaves in the second half of its array.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## The iterative bottom-up version

For point updates and commutative operations there is a compact, fast, non-recursive form. It needs only 2n slots, with the leaves in the second half:

```formula
leaf(j) = n + j
parent(i) = ⌊i / 2⌋
n = 8:  leaf(5) = 13,  parent(13) = 6
where
n: the number of elements in the array
j: an array position, from 0 to n − 1
leaf(j): the index in the tree array of element j's leaf
i: any tree index other than the root (index 1)
parent(i): the index of i's parent
⌊ ⌋: floor: round down to the nearest whole number
In words: element j is stored at slot n + j, and halving any index (rounding down) moves one level up.
```

In Python, `i // 2` is exactly the floor of i / 2 for non-negative i.

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
            # Include the exposed left-edge
            # block.
            res += t[l]
            l += 1
        if r & 1:   # r - 1 is a left child
            r -= 1
            # Include the exposed right-edge
            # block.
            res += t[r]
        l, r = l // 2, r // 2
    return res
```

It avoids recursive-call overhead.

> [!note] Content gap: performance multiplier
> No fixed speedup is supplied because the original “several times faster” claim lacked a reproducible benchmark for a specified implementation and workload.

## Where segment trees are used

- Competitive programming and interviews: range sum/min/max with updates, "count of smaller numbers after self" (after coordinate compression), and booking problems such as "maximum number of overlapping events" (range add plus range max).
- **Computational geometry**: sweep-line algorithms, such as computing the area of a union of rectangles, keep a segment tree over the y-coordinates.
- **Huge index ranges**: a dynamic (sparse) segment tree creates nodes only when touched, so it can cover indices up to 10^9 with memory proportional to the operations performed.

> [!note] A name clash
> In computational geometry, "segment tree" traditionally names a related structure that stores a set of *intervals* and answers "which intervals contain point x?" in O(log n + k), where n is the number of stored intervals and k is the number of intervals reported. The Wikipedia article describes that version. The array-based segment tree in this lesson is the meaning used in competitive programming and interviews.

## Pitfalls

- Inclusive vs half-open ranges. Pick one convention and stick to it; mixing them is the most common bug.
- **Wrong identity.** Returning 0 for a disjoint range in a *min* tree silently corrupts answers. Use +infinity.
- Forgetting to push. In a lazy tree, every operation that descends past a node must push its tag first, including queries.
- Overkill. If you only need prefix sums with point updates, a Fenwick tree (next lesson) is shorter and often has lower overhead; measure the actual workload. If the array never changes, a prefix-sum array or sparse table is simpler still.

## Key takeaways

- A bottom-up tree puts leaves in the second half of its array.
- Keep half-open ranges distinct from inclusive ranges and choose the simplest structure for the workload.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
