---
id: prob-sampling-confidence
title: Estimate uncertainty with standard errors and intervals
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: The standard error scales with the inverse square root of the iid sample size.
---

The spread of individual requests and the uncertainty in an estimated mean are different. **Standard deviation** describes individual variation; **standard error** describes variation of the estimator across repeated samples.

## More independent data reduces uncertainty

For independent identically distributed observations with finite variance, the standard error of the sample mean decreases with the square root of sample size. Quadrupling observations halves it; doubling observations does not.

```formula essential
SE = σ / √(n)
where
SE: the standard error, the typical distance between the sample mean x̄ and the true mean μ (mu)
σ: sigma, the standard deviation of a single observation, in the same units as the data
n: the positive integer number of independent identically distributed observations
√: the square root
In words: for independent identically distributed observations with finite variance, the sample mean's standard deviation is the individual standard deviation divided by the square root of sample size.
```

This scaling describes sampling variability, not a guaranteed realised error. More observations also cannot remove systematic sampling bias or repair an unrepresentative measurement window.

## Interpret an interval as a procedure

A **95% confidence interval** comes from a procedure intended to cover the fixed true value in 95% of repeated experiments under its assumptions. It is not a statement that 95% of individual requests lie inside, or that this one fixed interval has a 95% posterior probability of containing the parameter.

```formula reference
x̄ ± 1.96 × SE
where
x̄: "x-bar", the sample mean
±: plus or minus; the interval runs from x̄ − 1.96 × SE to x̄ + 1.96 × SE
SE: the standard error of the mean
1.96: the number of standard errors that captures the middle 95% of a normal distribution (2.5% is cut off in each tail)
In words: take the estimate and go about two standard errors either side.
```

The normal approximation requires a sufficiently accurate sampling approximation. A mean estimated from normal iid observations can use a Student-t interval when the standard deviation is estimated. For proportions, the simple Wald interval can perform poorly near zero or one or with few successes or failures; Wilson or exact binomial procedures offer alternatives.

## Check what counts as independent evidence

Many requests during one shared pause may provide less information than the same number spread across independent conditions. Positive correlation can make an independence-based standard error too small; the sign and structure of dependence matter.

Benchmark warm-up, noisy neighbours and changing conditions also matter. Repeat and interleave comparisons rather than giving every observation of one version an earlier environment. A narrow interval under a wrong sampling model can be misleading.

## Key takeaways
- Standard error concerns an estimator, not individual spread.
- Confidence coverage belongs to the repeated procedure.
- Sample size does not fix bias, dependence or a poor approximation.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
