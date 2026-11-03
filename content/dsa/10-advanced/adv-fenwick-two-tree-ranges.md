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

A tree of differences can recover one current element, but a prefix total must count each difference once for every later included position. Two trees separate that repeated contribution from its correction.

`b1` stores differences; `b2` stores each difference multiplied by the number of positions before it. Multiply the first tree's prefix by the query endpoint, then subtract the second tree's prefix. The correction removes positions that lie before each difference began.

```formula reference
P(i) = i P_1(i) − P_2(i)
where
i: the one-based endpoint of the requested prefix
P(i): the sum of the first i elements
P_1(i): the prefix sum of differences held in b1
P_2(i): the prefix sum of weighted differences held in b2; each difference is multiplied by its position minus one
In words: the first tree repeats each difference across the whole prefix; the second removes the positions before that difference actually starts.
```

For example, adding five to positions three through six of an initially zero array leaves positions one and two unchanged. A prefix ending at four includes two increased elements and totals ten; one ending at seven includes all four and totals twenty. Boundary cancellation makes later prefixes stop growing for that update. Several range additions combine by addition.

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
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
