---
id: cx-common-growth
sourceLesson: cx-growth-rates
title: Comparing growth rates
level: basic
minutes: 2
summary: Compare logarithmic, linear, quadratic and exponential operation counts.
---

A growth rate describes how work changes as the input becomes larger. It is a scaling prediction, not a stopwatch reading. Here n is the item count and each counted operation has constant cost.

## Recognise the behaviour

| Growth | What creates it | Effect of a larger input |
|---|---|---|
| Constant | fixed amount of work | no input-dependent increase |
| Logarithmic | repeatedly discard a fixed fraction | doubling adds roughly one halving step |
| Linear | visit every item once | doubling roughly doubles work |
| Linear times log | linear work over logarithmically many levels | doubling costs slightly more than twice |
| Quadratic | compare all pairs | doubling roughly quadruples work |
| Exponential | explore independent binary choices | each extra choice doubles candidates |

A base-two **logarithm** is the power needed to produce a value from two. For powers of two it also counts repeated halvings down to one. Ten halvings reduce 1,024 to one; doubling that starting size adds just one halving. For other sizes, an algorithm rounds its number of steps as its stopping rule requires.

The contrast between linear, quadratic and exponential growth is worth seeing directly:

```formula essential
W_linear(n) = n
W_pairs(n) = n^2
W_subsets(n) = 2^n
where
W_linear(n): an idealised count with one operation per input item
W_pairs(n): an idealised full ordered-pair count, including self-pairs
W_subsets(n): the number of subsets of n distinct items, assuming one check per subset
n: the nonnegative item count
In words: a scan grows with the item count, all-pairs work grows with its square, and adding one binary choice doubles the number of subsets.
```

The subset model counts candidates. If checking a candidate requires scanning its contents, include that cost too.

Small test inputs can conceal an expensive growth rate. Conversely, a small fixed input may make exhaustive search entirely sensible. There is no universal item cutoff for exponential algorithms: candidate cost, pruning, hardware and the available time all matter.

## Key takeaways
- Recognise how the work changes before calculating an exact count.
- Logarithmic growth comes from reducing the remaining problem by a fixed factor.
- Growth labels help compare scaling; measurements settle practical runtime.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
