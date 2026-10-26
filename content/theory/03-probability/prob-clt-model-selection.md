---
id: prob-clt-model-selection
title: Check a normal approximation and choose a model
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: The iid finite-variance CLT is a limiting statement.
---

Averages can become more stable and more nearly bell-shaped than individual observations. The **central limit theorem (CLT)** explains one important case, but it is not permission to treat every data set as normal.

## What approaches a normal distribution?

For independent identically distributed observations with finite nonzero variance, the centred and scaled sum, or equivalently the centred and scaled average, converges in distribution to a standard normal as the sample grows. This is a limiting statement; there is no universal sample size that guarantees accurate tail estimates.

The original observations do not thereby become normal. For independent copies with the same variance, the sum's standard deviation grows with the square root of the count, while the average's standard deviation shrinks with that square root. Quadrupling observations halves the average's standard deviation.

## Choose a model from the process

| Quantity | Candidate model |
|---|---|
| Success count in fixed independent equal-probability trials | Binomial |
| Independent equal-probability trials until success | Geometric |
| Count in a homogeneous Poisson-process window | Poisson |
| Standardised average meeting CLT assumptions | Approximate normal |

A binomial normal approximation needs enough expected successes and failures. A Poisson normal approximation improves as its mean grows. A **continuity correction** treats whole-number counts as intervals extending half a unit on either side, but does not repair invalid assumptions.

## Inspect latency tails directly

Mean and standard deviation do not determine high percentiles. Latency can be skewed or multimodal; nonnegativity alone proves neither skewness nor a heavy tail. A normal approximation may fit central observations while misrepresenting rare delays that matter to an SLO.

Use enough observations or an appropriate histogram to estimate the relevant tail and its uncertainty. Dependence, changing traffic and rare extreme values all require attention before trusting an approximation.

## Key takeaways
- The CLT concerns standardised sums or averages under stated assumptions.
- Large samples do not provide a universal tail-accuracy guarantee.
- Choose models by process and check the predictions that matter.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
