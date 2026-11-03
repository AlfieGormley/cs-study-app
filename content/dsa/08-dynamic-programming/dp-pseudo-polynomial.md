---
id: dp-pseudo-polynomial
title: Numeric value versus encoded input size
level: intermediate
minutes: 3
summary: A numeric capacity can be exponentially larger than its bit length.
sourceLesson: dp-knapsack
---

## Pseudo-polynomial time

0/1 knapsack takes O(n · W) time, where n is the number of items and W the weight limit. That looks polynomial. It isn't, quite.

Complexity is measured against the **size of the input**: the number of bits needed to write it. The input includes every weight and value as well as W, so their bit lengths all matter. Writing W in binary takes far fewer bits than W itself: one thousand needs only ten binary digits, yet the table needs 1,001 columns.

```formula reference
b = ⌊log_2(W)⌋ + 1
W < 2^b
T = O(nW)
T = O(n × 2^b)
where
b: the number of bits needed to write W in binary
W: the capacity, a positive whole number
log_2(W): the base-2 logarithm of W, the power you raise 2 to in order to get W
⌊x⌋: floor, x rounded down to a whole number
2^b: b copies of 2 multiplied together
T: the running time of the table algorithm
n: the number of items
O(...): Big-O, growing at most in proportion to the expression inside
In words: W is about 2 to the power of its bit length, so work proportional to W is exponential in the number of bits used to write it.
```

The capacity-based bound is therefore not polynomial in the full binary encoding length.

| Capacity | Bits | Work proxy: 100 items |
|---|---|---|
| 1,000 | 10 | 100,000 |
| 1,000,000 | 20 | 100,000,000 |
| 1,000,000,000 | 30 | 100 billion |
| 10¹⁸ | 60 | 10²⁰ |

Adding ten bits to W multiplies the work by about 1,000 (2¹⁰ = 1,024). An algorithm that's polynomial in the **numeric value** but not in its bit length is called **pseudo-polynomial**.

> [!analogy] Real-world analogy: tally marks versus digits
> Writing "1,000,000" takes seven digits, but counting it out in tally marks takes a million strokes. Adding one more digit to the number makes the tally ten times longer.
>
> **How it maps:** the input to an algorithm is the written number, so its size is the number of digits (bits, in binary). A capacity-indexed DP makes one column of its table for every unit of capacity, like drawing every tally mark. Its work grows with the number's value, which is exponential in the number of digits used to write it.
>
> **Where it stops:** computers write numbers in binary, so each extra bit doubles the value rather than multiplying it by ten. And unlike a tally, the DP's cost also multiplies by the number of items, and many practical instances have small enough capacities that it runs quickly.

This is consistent with knapsack, subset sum and partition being **NP-complete** (as decision problems). These decision versions are **weakly NP-complete**: they have pseudo-polynomial algorithms, unlike strongly NP-complete numeric problems, unless every problem whose solutions can be checked in polynomial time can also be solved in polynomial time, a statement widely believed to be false. Large numbers do not make every individual instance difficult. When the numbers are small (bounded by a polynomial in n), DP solves them efficiently. Contrast with *strongly* NP-hard problems like the travelling salesman, whose decision versions remain NP-complete even with polynomially bounded weights.

## Key takeaways
- A numeric capacity can be exponentially larger than its bit length.
- Capacity-indexed DP is pseudo-polynomial.
- Small numeric bounds can make weakly NP-complete problems manageable.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
