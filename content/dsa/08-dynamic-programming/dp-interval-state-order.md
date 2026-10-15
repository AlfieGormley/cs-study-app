---
id: dp-interval-state-order
title: Intervals, split points and cubic work
level: advanced
minutes: 3
summary: Interval dependencies are smaller ranges.
sourceLesson: dp-interval-tree
---

So far every state has been a prefix, a suffix or a pair of prefixes. Two more shapes cover a large class of harder problems:

- **Interval DP**: the state is an unbroken range `[i, j]`, and the recurrence splits it at some point k.
- **Tree DP**: the state is a node (often with a small flag), and the answer combines the answers of its children.

## Interval DP: the pattern

```formula
dp[i][j] = best of g(dp[i][k], dp[k + 1][j],
  cost(i, k, j))   for i ≤ k < j
T = O(n^2) × O(n) = O(n^3)
where
dp[i][j]: the answer for the unbroken range of elements i to j, inclusive
i, j: the first and last positions of the range, 0 ≤ i ≤ j ≤ n − 1
k: the split point: the left part is i to k and the right part is k + 1 to j
best: min or max, whichever the problem asks for, taken over every split point k
g: the problem's rule for combining the two parts' answers with the cost of joining them (often just adding them)
cost(i, k, j): the cost of the final step that joins the two parts
n: the number of elements in the whole sequence
T: the total running time
n^2: n × n, roughly the number of ranges (about n^2 / 2 of them)
n^3: n × n × n
O(...): Big-O, growing at most in proportion to the expression inside
In words: try every place to split the range, combine the best answers for the two pieces, and keep the best split; about n^2 ranges times about n splits each gives cubic time.
```

- **States**: O(n²) intervals.
- **Transitions**: O(n) split points each.
- **Total**: usually **O(n³)** time and O(n²) slots, for n sequence elements. The cubic bound is not an exact transition count. For the classic matrix-chain loops:

```formula
I = n(n − 1)(n + 1) / 6
I(500) = 20,833,250
where
I: the number of inner split candidates over all nonempty intervals
n: the number of matrices, a nonnegative whole number
In words: Each triple of two outer boundaries and an internal split is counted once; five hundred matrices try about twenty-one million splits.
```
- **Order**: every interval depends on strictly shorter ones, so loop by **length**, from short to long.

## Recognise the interval boundary

For an optimal search tree over sorted keys, the chosen root divides a key interval into the ranges on its left and right. CYK parsing splits a substring and combines two grammar symbols allowed by a rule. Cutting a rod at fixed marks chooses a first cut inside a piece; the two resulting marked intervals are independent, and that cut costs the original piece’s length. These have range states and split choices. LIS ending states and ordinary tree include/exclude states have different dependency shapes.

## Key takeaways
- Interval dependencies are smaller ranges.
- Increasing interval length is a valid evaluation order.
- Count all split candidates rather than equating a cubic bound with an exact count.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Matrix chain multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
