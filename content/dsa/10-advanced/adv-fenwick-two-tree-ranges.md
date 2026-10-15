---
id: adv-fenwick-two-tree-ranges
title: Range sums with two Fenwick trees
level: advanced
minutes: 3
summary: One tree stores differences and the other corrects their prefix weighting.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

### Range update, range query

Use two trees, `b1` and `b2`. For the code’s range-add arguments `l`, `r` and `x`, `b1` stores the difference-array boundaries and `b2` stores their position-weight corrections. The complete calls below show both updates to each tree. The prefix sum is then:

```formula
P(i) = i P_1(i) − P_2(i)
P_1(i) = x   when l ≤ i ≤ r
P_2(i) = x(l − 1)   when l ≤ i ≤ r
P(i) = xi − x(l − 1) = x(i − l + 1)
P_2(i) = x(l − 1) − xr   when i > r
P(i) = 0 − x(l − 1 − r) = x(r − l + 1)
P(4) = 5 × 4 − 5 × 2 = 10
P(7) = 0 × 7 − (10 − 30) = 20
where
i: the position the prefix sum ends at
P(i): the true sum of the first i elements
P_1(i): the prefix sum read from tree b1
P_2(i): the prefix sum read from tree b2, a correction term
l, r: the first and last positions of the range add
x: the amount added to each element in the range
≤: is at most
>: is greater than
In words: inside the range, b1 counts x for every position up to i, which is too much by the l − 1 positions before the range, and b2 subtracts exactly that; past the range, b2 alone leaves x times the range length.
```

Before the range both trees read 0, so the prefix sum is 0, as it should be. The last two lines are a worked example: add 5 to positions 3 to 6 of an 8-element array of zeros. At position 4 the answer is 10 (two elements of 5 so far); at position 7 it is 20 (all four elements of 5). Several range adds simply add up, because both trees are linear.

```python
class RangeFenwick:
    def __init__(self, n):
        self.b1 = Fenwick(n)
        self.b2 = Fenwick(n)

    def range_add(self, l, r, x):
        self.b1.add(l, x)
        self.b1.add(r + 1, -x)
        # Correct prefixes before the start.
        self.b2.add(l, x * (l - 1))
        # Cancel weighting beyond the range.
        self.b2.add(r + 1, -x * r)

    def prefix(self, i):
        return (self.b1.prefix(i) * i
                - self.b2.prefix(i))
```

`b1` is the difference array; `b2` is a correction so that positions before l and after r come out right.

## Key takeaways

- One tree stores differences and the other corrects their prefix weighting.
- Subtract prefix totals to recover any inclusive range total.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
