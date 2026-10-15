---
id: dp-large-knapsack-capacities
title: Alternative strategies for huge capacities
level: intermediate
minutes: 3
summary: Small total values suggest indexing by value instead of weight.
sourceLesson: dp-knapsack
---

A weight-indexed table can be too large even for a modest item count. Choose a different state or a different guarantee according to which quantity is small.

### What to do when W is huge

- **DP over value instead of weight**: `minW[v]` records minimum weight needed to achieve value exactly v. It takes O(n · V) time, where V is the total of all values. Useful when values are small but weights are big.
- **Meet in the middle**: for n up to about 40, split the items in half, enumerate all subsets of each half, sort one side and binary-search it:

```formula
T = O(n × 2^{⌈n/2⌉})
T(40) ≈ 2^20 × 20 ≈ 10^6 × 20 = 2 × 10^7
where
T: the running time, in basic steps
n: the number of items
2^{⌈n/2⌉}: the subset count of the larger half when n is odd
⌈x⌉: ceiling, the smallest integer not less than x
x: the quantity being rounded upwards
O(...): Big-O, growing at most in proportion to the expression inside
≈: approximately equal to
In words: each half has only 2^(n/2) subsets, and sorting plus binary search adds about a factor of n, so the work never depends on W.
```

With forty items, the displayed work proxy is about twenty million steps, compared with about 1.1 trillion subsets for full enumeration. These estimates omit implementation constants and integer bit costs.

- **Approximation algorithms**: scale and round the values, then run the value DP. Pick an allowed relative error ε (epsilon) between 0 and 1. For nonnegative values, discard individually overweight items, choose an appropriate scaling factor and handle the zero-optimum case separately. The appropriately scaled value DP has the following guarantee:

```formula
A ≥ (1 − ε)OPT
0 < ε < 1
where
A: the value obtained by the approximation algorithm
OPT: the largest feasible total value
ε: epsilon, the chosen relative-error tolerance
≥: greater than or equal to
In words: The returned value loses at most the chosen fraction of the optimum.
```

For a one-percent tolerance the returned value is at least 99 percent of the optimum. With n items, its work is polynomial in n and the reciprocal of the tolerance, plus input bit costs: an FPTAS. The correct scaling construction is required; arbitrary rounding does not establish this guarantee.
- **Branch and bound / integer programming** solvers can exploit structure in some large instances, but retain exponential worst-case risks.

## Key takeaways
- Small total values suggest indexing by value instead of weight.
- Meet in the middle reduces dependence on the item count.
- Approximation and exact solvers have different guarantees.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
