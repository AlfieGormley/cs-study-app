---
id: prob-poisson-counts
title: Model Poisson counts and rare-trial approximations
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: A Poisson parameter is an expected count in a specified window.
---

A **Poisson distribution** describes a nonnegative whole-number count. Its parameter is the expected count in a specified window, so “three per hour” and “three per minute” cannot be substituted without changing the window.

## Where the model comes from

An exact example is the count during a fixed window of a homogeneous **Poisson process**: a process with constant intensity and independent increments. A suitable collection of many independent rare opportunities can also have an approximately Poisson count.

An average of three events per hour does not mean three arrive every hour. Quiet windows and bursts are possible even in a constant-rate model. Increasing the window's expected count reduces its chance of being empty.

```formula reference
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
In words: within a Poisson model, the expected count determines every count probability; it also equals the count variance.
```

At expected count zero, the count is always zero. This is a separate deterministic endpoint of the model.

## Test a proposed approximation

A binomial count can be approximated by a Poisson count when there are many trials with small individual success probabilities. Use the same expected count. Fair coin tosses do not have rare successes, so this is not generally a good approximation to their head count.

The Poisson mean equals its variance. Substantially larger observed count variance, called **overdispersion**, is a warning: bursts, varying intensity or mixed populations may invalidate a single Poisson model. Sample estimates vary, and mean–variance agreement alone does not establish the distribution.

Retries until success are a waiting-time question, not events per window. Always specify what the random quantity counts before selecting a distribution.

## Key takeaways
- Attach an explicit window to a Poisson expected count.
- Independent rare trials can motivate an approximation.
- A stable average alone does not establish a Poisson process.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
