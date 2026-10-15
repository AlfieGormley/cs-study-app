---
id: adv-segment-combine-summaries
title: Combining summaries and maximum subarrays
level: advanced
minutes: 4
summary: An associative combine and an empty-range identity define a valid range summary.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Beyond sums: what can a node store?

The structure works whenever the combine operation is **associative**, with an **identity element** for the empty range:

```formula
(x ⊕ y) ⊕ z = x ⊕ (y ⊕ z)
x ⊕ e = e ⊕ x = x
min(min(5, 2), 8) = min(5, min(2, 8)) = 2
where
⊕: the combine operation the tree uses (for example +, min or max)
x, y, z: any three node summaries, in left-to-right order
e: the identity element: the value that leaves anything unchanged when combined with it (0 for +, +∞ for min, −∞ for max)
min: the smaller of its arguments
+∞: plus infinity, larger than every value
−∞: minus infinity, smaller than every value
In words: you may group neighbouring pieces in any way without changing the answer, and there is a neutral value to return for an empty range.
```

The worked line shows min is associative. Sum, min, max, gcd (greatest common divisor), bitwise AND, bitwise OR, bitwise XOR and matrix products all qualify. Subtraction does not: subtracting three and then two from eight gives three, while subtracting their difference from eight gives seven.

Associative is enough; commutative is not required. The recursive code always combines the left child before the right, so non-commutative operations like matrix multiplication or string concatenation work, as long as you keep that order. Actual string concatenation is not constant-time, and matrix costs depend on dimension; their runtimes include combine costs.

You can also store a small **struct** per node. The famous example is the **maximum subarray sum** over a range, with point updates. Each node stores four numbers:

| Field | Symbol | Meaning |
|---|---|---|
| `sum` | s | total of the range |
| `pre` | p | best prefix sum |
| `suf` | q | best suffix sum |
| `best` | b | best subarray sum |

Combining a left child L and a right child R:

```formula
s = s_L + s_R
p = max(p_L, s_L + p_R)
q = max(q_R, s_R + q_L)
b = max(b_L, b_R, q_L + p_R)
where
s, p, q, b: the combined node's total, best prefix sum, best suffix sum and best subarray sum
s_L, p_L, q_L, b_L: the same four numbers for the left child L
s_R, p_R, q_R, b_R: the same four numbers for the right child R
max: the largest of its arguments
In words: the best prefix either stays in the left half or takes all of it plus a prefix of the right; the best subarray is in one half or is a left suffix joined to a right prefix.
```

For example, take the left half [2, −1] and the right half [3, −5]:

```formula
s_L = 1,  p_L = 2,  q_L = 1,  b_L = 2
s_R = −2,  p_R = 3,  q_R = −2,  b_R = 3
s = 1 + (−2) = −1
p = max(2, 1 + 3) = 4
q = max(−2, −2 + 1) = −1
b = max(2, 3, 1 + 3) = 4
where
s_L, p_L, q_L, b_L: total, best prefix, best suffix and best subarray sum of the left half [2, −1]
s_R, p_R, q_R, b_R: the same four numbers for the right half [3, −5]
s, p, q, b: the same four numbers for the whole array [2, −1, 3, −5]
max: the largest of its arguments
In words: the best subarray of the whole array is 2 − 1 + 3 = 4, which crosses the middle and is found as the left half's best suffix plus the right half's best prefix.
```

You can check every line by listing the prefixes and suffixes of [2, −1, 3, −5] by hand. These rules assume subarrays must be non-empty.

The best subarray is either entirely in one half or crosses the middle, in which case it is a suffix of the left plus a prefix of the right. Kadane's algorithm cannot handle updates; this can, in O(log n) each.

## Key takeaways

- An associative combine and an empty-range identity define a valid range summary.
- Maximum-subarray nodes retain total, best prefix, best suffix and best interior sum.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
