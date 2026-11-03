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

Associativity means adjacent pieces can be grouped differently without changing the result. An identity is a neutral summary that leaves another summary unchanged: zero for sums, positive infinity for minima, and negative infinity for maxima.

Sum, min, max, gcd (greatest common divisor), bitwise AND, bitwise OR, bitwise XOR and matrix products all qualify. Subtraction does not: subtracting three and then two from eight gives three, while subtracting their difference from eight gives seven.

Associative is enough; commutative is not required. The recursive code always combines the left child before the right, so non-commutative operations like matrix multiplication or string concatenation work, as long as you keep that order. Actual string concatenation is not constant-time, and matrix costs depend on dimension; their runtimes include combine costs.

You can also store a small **struct** per node. The famous example is the **maximum subarray sum** over a range, with point updates. Each node stores four numbers:

| Field | Symbol | Meaning |
|---|---|---|
| `sum` | s | total of the range |
| `pre` | p | best prefix sum |
| `suf` | q | best suffix sum |
| `best` | b | best subarray sum |

To combine children, add their totals. A prefix either stays in the left child or includes the whole left child plus a right prefix; a suffix works symmetrically. The best subarray either stays in one child or crosses the split, joining a left suffix to a right prefix. The exact update rules are useful implementation reference:

```formula reference
s = s_L + s_R
p = max(p_L, s_L + p_R)
q = max(q_R, s_R + q_L)
b = max(b_L, b_R, q_L + p_R)
where
s, p, q, b: the combined total, best prefix sum, best suffix sum and best non-empty subarray sum
s_L, p_L, q_L, b_L: those four summaries for the left child
s_R, p_R, q_R, b_R: those four summaries for the right child
max: the largest argument
In words: a prefix either stays in the left half or includes that whole half; a suffix is symmetric. The best subarray stays in one half or joins a left suffix to a right prefix.
```

For example, take the left half [2, −1] and the right half [3, −5]:

The best subarray of `[2, -1, 3, -5]` is `[2, -1, 3]`, with total 4. It crosses the split: the best suffix of the left half joins the best prefix of the right half.

These rules assume non-empty subarrays. For an empty-range identity use a total of zero and negative infinity for the other three fields; a real leaf uses its value for all four fields.

The best subarray is either entirely in one half or crosses the middle, in which case it is a suffix of the left plus a prefix of the right. Kadane's algorithm cannot handle updates; this can, in O(log n) each.

## Key takeaways

- An associative combine and an empty-range identity define a valid range summary.
- Maximum-subarray nodes retain total, best prefix, best suffix and best interior sum.

## Further reading
- [Segment trees — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
