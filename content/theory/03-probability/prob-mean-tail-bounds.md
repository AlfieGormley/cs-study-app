---
id: prob-mean-tail-bounds
title: Bound tails from mean and variance
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Markov needs a nonnegative variable and a positive threshold.
---

A mean does not determine how often extreme values occur, but it can constrain them. A **tail bound** gives a limit, not the exact tail probability.

## A budget argument for nonnegative quantities

**Markov’s inequality** applies to a nonnegative variable with known finite mean and a positive threshold. Every observation above the threshold consumes at least that much of the average's total budget. Too many such observations would force the mean higher.

```formula reference
P(X ≥ a) ≤ E[X] / a
where
P: probability of measurable events, dimensionless and between zero and one
X: a random variable that is never negative, with a finite mean
a: any positive threshold in the same units as X
P(X ≥ a): the probability that X is at least a
E[X]: the expected value (mean) of X
≥: greater than or equal to
≤: less than or equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: For a nonnegative quantity, divide its finite mean by a positive threshold to bound the probability of reaching or exceeding that threshold.
```

For nonnegative latency with mean 20 milliseconds, at most 20% can be at least 100 milliseconds. That bound could be attained by putting 20% exactly at the threshold and the rest at zero. Another distribution with the same mean could have no observations at that threshold. The mean alone cannot distinguish them.

## Variance adds information about deviations

**Chebyshev’s inequality** bounds deviations on either side of the mean using finite variance. At two standard deviations, at most one-quarter of the probability can lie that far or farther from the mean; the usual form assumes a positive standard deviation. A zero-variance variable is constant with probability one and can be treated separately.

Neither inequality requires a normal distribution. Chebyshev is not automatically tighter than every Markov bound: they use different information and may describe different events. Stronger assumptions about a distribution can yield tighter bounds, but must be justified.

## Key takeaways
- An upper bound is not an estimated or exact tail probability.
- Markov requires nonnegativity and a finite mean.
- Chebyshev uses variance without assuming a bell curve.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
