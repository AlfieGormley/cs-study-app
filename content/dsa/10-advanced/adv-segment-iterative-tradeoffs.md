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

For point updates and commutative operations there is a compact non-recursive form. For n input elements it uses `2 * n` slots: element `a[j]` lives at `t[n + j]`. The parent of an index `i` is `i // 2`. The code below builds the tree and answers half-open ranges, including an empty range.

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

Benchmark recursive and iterative implementations on the intended workload before claiming a speedup.

## Where segment trees are used

- Competitive programming and interviews: range sum/min/max with updates, "count of smaller numbers after self" (after coordinate compression), and booking problems such as "maximum number of overlapping events" (range add plus range max).
- **Computational geometry**: sweep-line algorithms, such as computing the area of a union of rectangles, keep a segment tree over the y-coordinates.
- **Huge index ranges**: a dynamic (sparse) segment tree creates nodes only when touched, so it can cover indices up to a billion with memory proportional to the operations performed.

> [!note] A name clash
> In computational geometry, "segment tree" traditionally names a related structure that stores a set of *intervals* and answers "which intervals contain point x?" in O(log n + k), where n is the number of stored intervals and k is the number of intervals reported. The array-based segment tree in this lesson is the meaning used in competitive programming and interviews.

## Pitfalls

- Inclusive vs half-open ranges. Pick one convention and stick to it; mixing them is the most common bug.
- **Wrong identity.** Returning 0 for a disjoint range in a *min* tree silently corrupts answers. Use +infinity.
- Forgetting to push. In a lazy tree, every operation that descends past a node must push its tag first, including queries.
- Overkill. If you only need prefix sums with point updates, a Fenwick tree (next lesson) is shorter and often has lower overhead; measure the actual workload. If the array never changes, a prefix-sum array or sparse table is simpler still.

## Key takeaways

- A bottom-up tree puts leaves in the second half of its array.
- Keep half-open ranges distinct from inclusive ranges and choose the simplest structure for the workload.

## Further reading
- [Segment trees — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Interval stabbing with segment trees — National Tsing Hua University](https://www.cs.nthu.edu.tw/~wkhon/ds/ds10/tutorial/tutorial6.pdf)
