---
id: prob-mean-tail-bounds
title: Bound tails from mean and variance
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Markov needs a nonnegative variable and a positive threshold.
---

## Markov's inequality: a free tail bound

Expectation alone gives a crude but guaranteed bound on the **tail probability**, the chance of a large value.

```formula
P(X ≥ a) ≤ E[X] / a
P(L ≥ 100 ms) ≤ (20 ms) / (100 ms)
P(L ≥ 100 ms) ≤ 0.2
where
P: probability of measurable events, dimensionless and between zero and one
X: a random variable that is never negative, with a finite mean
a: any positive threshold in the same units as X
P(X ≥ a): the probability that X is at least a
E[X]: the expected value (mean) of X
L: a nonnegative request latency, with mean 20 milliseconds (ms)
ms: millisecond, one thousandth of a second
≥: greater than or equal to
≤: less than or equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: a non-negative quantity can be at least a only a fraction E[X]/a of the time, otherwise its average would be too high.
```

If mean request latency is 20 ms, at most 20% of requests can take 100 ms or more. The true tail can be smaller or attain this bound. For a useful finite bound, Markov needs a nonnegative variable and a known finite mean. It is used to turn expected running time into a "with probability at least 1/2" statement.

**Chebyshev's inequality** bounds deviations in both directions using the variance:

```formula
P(|X − μ| ≥ k × σ) ≤ 1 / k^2
where
X: a random variable with finite, non-zero variance
μ: mu, the mean of X
σ: sigma, the standard deviation of X (the square root of its variance)
k: how many standard deviations away from the mean; any number greater than 0
|X − μ|: the absolute value of X − μ, the distance from the mean ignoring direction
P: probability; probabilities are dimensionless and apply to measurable events
≥: greater than or equal to
≤: less than or equal to
Conditioning: every event to the right of a given bar in this card has positive probability
In words: X is at least k standard deviations from its mean at most 1/k² of the time; for k = 3, at most 1/9, about 11%.
```

It need not improve every Markov bound at every threshold.

## Key takeaways
- Markov needs a nonnegative variable and a positive threshold.
- Chebyshev needs a finite positive variance; neither bound assumes normality.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
