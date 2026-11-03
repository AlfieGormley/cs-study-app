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

Start the extra increase at the range's left boundary and cancel it just after the right boundary. Differences inside the range do not change: both neighbours increased by the same amount. Summing differences reconstructs any element, taking the value before position one as zero.

In code that is `add(l, x)` and `add(r + 1, -x)`, and `prefix(i)` returns the current value at position `i`. Example: on 6 zeros, adding 5 to positions 2 to 4 gives differences [0, 5, 0, 0, −5, 0], whose running totals are [0, 5, 5, 5, 0, 0].

## Key takeaways

- A range addition changes only two difference-array boundaries.
- A prefix sum of the differences reconstructs one current element.

## Further reading
- [Fenwick trees — cp-algorithms](https://cp-algorithms.com/data_structures/fenwick.html)
