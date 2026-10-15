---
id: prob-sampling-confidence
title: Estimate uncertainty with standard errors and intervals
level: advanced
minutes: 4
sourceLesson: prob-statistics
summary: The standard error scales with the inverse square root of the iid sample size.
---

## Sampling and the standard error

You rarely measure everything; you measure a **statistical sample** and estimate. The sample mean estimates the true (population) mean. How far off is it likely to be?

For independent, identically distributed observations with a finite standard deviation, the **standard error** of the mean is:

```formula
SE = σ / √(n)
where
SE: the standard error, the typical distance between the sample mean x̄ and the true mean μ (mu)
σ: sigma, the standard deviation of a single observation, in the same units as the data
n: the positive integer number of independent identically distributed observations
√: the square root
In words: averaging n independent observations shrinks the typical error by a factor of the square root of n.
```

For example, with a single-request standard deviation of 80 ms, 100 requests give a standard error of 8 ms and 400 requests give 4 ms.

Quadrupling the sample halves the standard error; the realised estimation error is still random. That square root is the central fact of measurement: precision gets expensive fast.

## Confidence intervals

Under suitable **central limit theorem (CLT)** conditions and a large enough sample for the approximation, the sample mean is approximately normal. An approximate **95% confidence interval** is:

```formula
x̄ ± 1.96 × SE
where
x̄: "x-bar", the sample mean
±: plus or minus; the interval runs from x̄ − 1.96 × SE to x̄ + 1.96 × SE
SE: the standard error of the mean
1.96: the number of standard errors that captures the middle 95% of a normal distribution (2.5% is cut off in each tail)
In words: take the estimate and go about two standard errors either side.
```

> [!example] Latency benchmark
> 400 requests, mean 250 ms, sample **standard deviation (SD)** 80 ms.

```formula
SE = (80 ms) / √(400)
SE = (80 ms) / 20 = 4 ms
1.96 × SE = 1.96 × 4 ms ≈ 7.8 ms
CI = 250 ms ± 7.8 ms
CI ≈ 242 ms to 258 ms
where
SE: the standard error of the mean latency, in milliseconds (ms)
80: the sample standard deviation of one request's latency, in ms
400: the number of requests measured
√: the square root
1.96: the 95% multiplier for a normal distribution
CI: the 95% confidence interval
±: plus or minus
ms: milliseconds
≈: approximately equal to
In words: 400 requests pin the mean latency down to about ±8 ms.
```

For an **independent and identically distributed (iid)** Bernoulli **proportion**, the estimated standard error is:

```formula
SE = √((p̂(1 − p̂)) / n)
SE = √((0.05 × 0.95) / 10,000) ≈ 0.0022
CI ≈ 0.05 ± 1.96 × 0.0022
CI ≈ 0.046 to 0.054
where
p̂: "p-hat", the observed proportion, for example the fraction of visitors who converted; 0.05 (5%) here
n: the positive integer number of iid Bernoulli trials (visitors), 10,000 here
SE: the estimated standard error of the proportion; the interval approximation requires adequate successes and failures
CI: the approximate 95% confidence interval
√: the square root
±: plus or minus
1.96: the 95% normal multiplier
≈: approximately equal to
In words: a 5% rate measured on 10,000 visitors is uncertain by about 0.22 percentage points, so the 95% interval is roughly 4.6% to 5.4%.
```

The resulting **Wald interval** can be inaccurate near 0 or 1 or with small success/failure counts; Wilson or exact binomial intervals are alternatives. For a mean with an estimated standard deviation, a **Student-t interval** is exact under normal iid sampling and approaches the displayed normal interval for large samples.

> [!note] What "95% confidence" means
> It is a statement about the procedure: if you repeated the experiment many times, about 95% of the intervals you computed would contain the true value. It does **not** mean "there is a 95% probability the true value is in this particular interval" (a Bayesian credible interval can make a posterior-probability statement under its prior and likelihood model).

These formulas assume independent observations. Requests from the same user, or latencies during the same **garbage collection (GC)** pause, can be positively correlated, making an independence-based standard error too small. Correlation does not invariably increase uncertainty; its sign and structure matter. Benchmarks also suffer from warm-up effects and noisy neighbours, so run them repeatedly and interleave A and B rather than running all of A first.

## Key takeaways
- The standard error scales with the inverse square root of the iid sample size.
- Confidence describes repeated-procedure coverage.
- Approximation quality and dependence can invalidate naive intervals.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
