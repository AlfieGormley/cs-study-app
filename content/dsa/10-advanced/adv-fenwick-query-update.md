---
id: adv-fenwick-query-update
title: Fenwick query and update walks
level: advanced
minutes: 4
summary: Queries remove the lowest set bit to move to an earlier block.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

## The code

Assume n (the array length) is zero or more, update positions and ranges are valid 1-based positions, and a prefix query asks for anything from 0 to n elements. `add(n + 1, delta)` is an intentional no-op used by range-update boundaries. Complexity counts constant-time word arithmetic; arbitrary-size integer arithmetic has additional bit costs.

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        # 1-indexed
        self.t = [0] * (n + 1)

    def add(self, i, delta):
        # a[i] += delta
        while i <= self.n:
            self.t[i] += delta
            # Jump to the next enclosing
            # block.
            i += i & -i

    def prefix(self, i):
        # a[1] + ... + a[i]
        s = 0
        while i > 0:
            s += self.t[i]
            # Remove this block from the
            # prefix.
            i -= i & -i
        return s

    def range_sum(self, l, r):
        return (self.prefix(r)
                - self.prefix(l - 1))
```

### Querying: strip the lowest bit

`prefix(i)` adds `t[i]`, then removes i's lowest bit to jump to the end of the previous block, and repeats until i is 0:

```formula
i_next = i − lowbit(i)
13 − lowbit(13) = 13 − 1 = 12
12 − lowbit(12) = 12 − 4 = 8
8 − lowbit(8) = 8 − 8 = 0
P(13) = t[13] + t[12] + t[8]
where
i: the current index, starting at the number of prefix elements requested
i_next: the next index to visit
lowbit(i): the value of the lowest 1-bit of i
t[i]: the stored block sum at index i
P(13): the sum of the first 13 elements
In words: subtracting the lowest bit jumps to the end of the block just before the current one, so the query reads t[13] (a[13]), t[12] (a[9] to a[12]) and t[8] (a[1] to a[8]).
```

In binary the walk clears the lowest set bit at each step: the prefixes visit indices thirteen, twelve, eight and then zero. The earlier block-count bound shows this is logarithmic in the array length.

### Updating: add the lowest bit

`add(i, delta)` must change every block that contains position i. Those are `t[i]`, then `t[i + lowbit(i)]`, and so on: adding the lowest bit jumps to the next larger block that also covers i.

```formula
i_next = i + lowbit(i)
5 + lowbit(5) = 5 + 1 = 6
6 + lowbit(6) = 6 + 2 = 8
8 + lowbit(8) = 8 + 8 = 16
16 + lowbit(16) = 32 > n = 16
where
i: the current index, starting at the position being changed
i_next: the next index to update
lowbit(i): the value of the lowest 1-bit of i
n: the length of the array, 16 in this example
>: is greater than, so the loop stops
In words: adding the lowest bit climbs to the next, longer block that still contains the position, until the index passes the end of the array.
```

So `add(5, d)`, with d the value added, changes `t[5]` (element 5), `t[6]` (elements 5 to 6), `t[8]` (elements 1 to 8) and `t[16]` (elements 1 to 16). Each step moves the lowest set bit at least one place left, so this is also O(log n): the number of steps grows with the logarithm of the array length n.

> [!warning] Fenwick trees are 1-indexed
> Index 0 has lowbit 0, so `i += i & -i` would loop forever on `add(0, ...)`. Store `a[k]` at `k + 1` if your data is 0-indexed, and do the shift in one place.

## Key takeaways

- Queries remove the lowest set bit to move to an earlier block.
- Updates add the lowest set bit to visit enclosing blocks; index zero is invalid for updates.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
