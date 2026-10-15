---
id: prob-clt-model-selection
title: Check a normal approximation and choose a model
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: The iid finite-variance CLT is a limiting statement.
---

## Why it is everywhere: the central limit theorem

One standard **central limit theorem (CLT)** says that the centred and scaled sum of independent, identically distributed variables with finite, nonzero variance converges in distribution to a standard normal as the sample size grows. This motivates a large-sample normal approximation; independence and finite variance alone are not sufficient for arbitrary non-identically distributed sequences, and no universal finite sample size guarantees accurate tails.

Roll 100 independent fair six-sided dice. Each has mean 3.5 and variance 35/12, and means and (for independent variables) variances add:

```formula
E[S] = 100 × 3.5 = 350
Var(S) = 100 × 35/12 ≈ 291.7
σ = √(291.7) ≈ 17.1
1.96 × σ ≈ 34
where
S: the sum of the 100 dice
E[S]: its expected value
Var(S): its variance
σ: sigma, the standard deviation of S
√: the square root
1.96: the z-score for the middle 95% of a normal distribution
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: the sum centres on 350 and typically varies by about 17, so about 95% of the time it lands within 34 of 350.
```

The sum is close to normal, so about 95% of the time it lands within 350 ± 34 (exact enumeration gives 95.7% between 316 and 384).

The binomial has a useful normal approximation when both the expected successes and the expected failures are sufficiently large; the Poisson approaches normal as its mean grows. Check tail accuracy and use a **continuity correction** (treating each whole-number count as an interval extending half a unit on each side) for discrete counts.

```formula
Bin(n, p) ≈ N(n × p, n × p × (1 − p))
Bin(1000, 0.02) ≈ N(20, 4.4^2)
where
Bin(n, p): binomial with n trials and success probability p
N(μ, σ^2): normal with mean μ and variance σ^2
n: the number of trials; 1,000 disks in the second line
p: the success probability; 0.02 in the second line
4.4: the standard deviation √(1000 × 0.02 × 0.98)
≈: approximately distributed as
In words: the disk-failure count behaves roughly like a bell curve centred on 20 with standard deviation 4.4.
```

> [!warning] Check latency tails before choosing a model
> Latency can be right-skewed, multimodal or heavy-tailed, but none of these properties follows merely from being nonnegative. Right skew also does not imply a heavy tail. A normal approximation may misestimate high percentiles; inspect measured distributions and enough tail observations before using it for an **SLO** (service level objective, a target such as "99% of requests under 200 ms"). Mean and standard deviation alone do not determine the tail.

## Choosing a distribution

1. **Fixed number of independent tries with the same success probability, count successes?** Binomial.
2. **Independent constant-probability trials until success?** Geometric. Waiting for the next event in a homogeneous Poisson process? Exponential distribution.
3. **Count independent rare events at a stable rate?** Consider a Poisson model and check its assumptions.
4. **A standardised sum or average meeting CLT conditions?** Consider a normal approximation and check finite-sample accuracy.
5. **Check the assumptions.** Independence and constant rates are the usual casualties: retries cluster, traffic is diurnal, failures cascade.

In Python, `scipy.stats` provides all of these (`binom`, `geom`, `poisson`, `norm`) with `cdf` and `sf` (survival function, 1 − cdf) methods. Discrete distributions provide `pmf`; the continuous normal provides `pdf` instead. Use `sf` directly for small upper-tail probabilities to reduce cancellation error. The standard library has `statistics.NormalDist`.

## Key takeaways
- The iid finite-variance CLT is a limiting statement.
- Finite-sample tail accuracy needs checking.
- Mean and standard deviation alone do not determine latency tails.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
