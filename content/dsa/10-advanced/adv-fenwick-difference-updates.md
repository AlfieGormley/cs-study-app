---
id: adv-fenwick-difference-updates
title: Range additions through difference arrays
level: advanced
minutes: 2
summary: A range addition changes only two difference-array boundaries.
sourceLesson: adv-fenwick-trees
---

Here n is the number of input elements. Fenwick positions start at 1; the empty prefix is valid, but an update at zero is not. Arithmetic costs assume word-sized values.

## Variations

### Range update, point query

Store a **difference array** in the tree: each entry holds how much an element differs from the one before it. Then a range add touches only two entries, and an element's value is a prefix sum:

```formula
d[k] = a[k] − a[k − 1]
a[i] = d[1] + d[2] + … + d[i]
d[l] ← d[l] + x
d[r + 1] ← d[r + 1] − x
where
a[k]: the current value at position k (a[0] is taken as 0)
d[k]: the difference between position k and the one before it
i: the position whose value is wanted
l, r: the first and last positions of the range being increased
x: the amount added to every element from l to r
←: "becomes": replace the left side with the right side
…: every term in between
In words: adding x to a range only changes the step up at its start and the step down just after its end, and summing the steps rebuilds any value.
```

In code that is `add(l, x)` and `add(r + 1, -x)`, and `prefix(i)` returns the current value of a_i. Example: on 6 zeros, adding 5 to positions 2 to 4 gives differences [0, 5, 0, 0, −5, 0], whose running totals are [0, 5, 5, 5, 0, 0].

## Key takeaways

- A range addition changes only two difference-array boundaries.
- A prefix sum of the differences reconstructs one current element.

## Further reading
- [Fenwick Tree — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
- [Fenwick tree — Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree)
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
