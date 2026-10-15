---
id: prob-poisson-counts
title: Model Poisson counts and rare-trial approximations
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: A Poisson parameter is an expected count in a specified window.
---

## Poisson: counting rare events in a window

Many independent rare opportunities can yield an approximately **Poisson** count. An exact example is the count in a window of fixed length of a homogeneous Poisson process, with constant intensity and independent increments. The Poisson parameter λ is the expected count in that window, not a rate with unspecified units:

```formula
P(X = k) = (λ^k e^{−λ}) / k!
E[X] = λ
Var(X) = λ
where
P: probability of measurable events, dimensionless and between zero and one
X: the number of events in the window (0, 1, 2, …)
k: a nonnegative integer count we ask about
λ: lambda, the positive expected count in the window for the displayed mass formula; the zero-mean case is described below
P(X = k): the probability of exactly k events
e: Euler's number, about 2.718, the base of natural logarithms; e^{−λ} is the chance of no events at all
λ^k: λ multiplied by itself k times
!: factorial; k! = k × (k − 1) × … × 1, and 0! = 1
E[X]: the expected count
Var(X): the variance of the count
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: the chance of exactly k events depends only on the expected count λ; the mean and the variance are both λ.
```

At mean zero the count is zero with probability one. This degenerate case is defined separately to avoid an ambiguous zero-to-zero power.

For example, with 2 errors expected per hour:

```formula
P(X = 0) = e^{−2} ≈ 0.135
P(X = 2) = (2^2 e^{−2}) / 2! ≈ 0.271
where
X: the number of errors in one hour, Poisson with mean λ = 2
λ: lambda, the expected count in the one-hour window, 2; a dimensionless count
P: probability; probabilities are dimensionless and apply to measurable events
e: Euler's number, about 2.718
!: factorial; 2! = 2 × 1 = 2
≈: approximately equal to
In words: an hour with no errors happens about 13.5% of the time, and an hour with exactly two errors about 27%.
```

The mean equals the variance, a handy diagnostic. If your measured counts have variance much bigger than the mean ("overdispersion"), a single Poisson model does not match that dispersion. Bursts, changing intensity or heterogeneous populations are possible causes. Mean–variance equality alone does not establish a Poisson distribution.

## Poisson approximates binomial

When there are many trials and each has a small success probability, the binomial count is close to a Poisson count with the same mean.

```formula
Bin(n, p) ≈ Poisson(λ)   if λ = n × p
P(L = 0) ≈ e^{−1} ≈ 0.368
P(L ≥ 2) ≈ 1 − 2 × e^{−1} ≈ 0.264
where
Bin(n, p): binomial with n trials, success probability p
Poisson(λ): the Poisson distribution with mean λ (lambda)
n: the number of trials, large; 100 packets here
p: the per-trial probability, small; 0.01 here
λ: lambda, the matching mean, n × p = 1 for the packets
L: the number of lost packets
e: Euler's number, about 2.718
P: probability; probabilities are dimensionless and apply to measurable events
≥: greater than or equal to
≈: approximately equal to
In words: for 100 packets at 1% loss, the Poisson shortcut gives 0.368 for no loss and 0.264 for two or more, almost identical to the exact binomial 0.366 and 0.264.
```

## Key takeaways
- A Poisson parameter is an expected count in a specified window.
- A Poisson approximation needs a suitable independent rare-event model.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
