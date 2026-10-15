---
id: prob-ab-sample-planning
title: Plan an A/B sample size
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: Choose effect size, significance and power before collecting the sample.
---

## Sample size: decide before you start

To detect a change from 10% to 11% conversion with a two-sided significance level of 0.05 and 80% power, the standard normal-approximation planning formula gives the users needed in each arm:

```formula
n ≈ (z_{0.975} + z_{0.8})^2
  × ((p_1 q_1 + p_2 q_2) / δ^2)
n ≈ (1.96 + 0.84)^2
  × ((0.09 + 0.0979) / 0.01^2)
n ≈ (7.84 × 0.1879) / 0.0001 ≈ 14,732
where
n: the number of users needed in each arm
z_{0.975}: 1.96, the standard normal value with 97.5% below it; it sets the two-sided 5% significance level
z_{0.8}: about 0.84, the standard normal value with 80% below it; it sets 80% power
p_1, p_2: the baseline and target conversion rates, 0.10 and 0.11
q_1, q_2: one minus each rate, 0.90 and 0.89; so p_1 × q_1 = 0.09 and p_2 × q_2 = 0.0979
δ: delta, the difference to detect, 0.11 − 0.10 = 0.01
≈: approximately equal to; 14,731.4 is rounded up because users come in whole numbers (unrounded z values give about 14,750)
In words: detecting a 1-point lift on a 10% base needs roughly 15,000 users per arm.
```

Using approximately equal arm variances gives a handy planning rule:

```formula
n ≈ (16p(1 − p)) / δ^2
n ≈ (16 × 0.1 × 0.9) / 0.01^2 = 14,400
where
n: users per arm
p: the baseline rate, 0.10
δ: delta, the difference to detect, 0.01
16: about 2 × (1.96 + 0.84)^2 = 15.7, rounded up; it bakes in 5% significance and 80% power
≈: approximately equal to
In words: sixteen times the per-user variance divided by the squared effect gives a quick sample-size estimate.
```

Notice the effect size is squared in the denominator: **halving the effect you want to detect quadruples the sample size**. Low traffic may make the required sample impractical within a stable experiment window; looking for a trend does not replace adequate sample size. This is an approximate planning formula, not an exact power guarantee.

## Key takeaways
- Choose effect size, significance and power before collecting the sample.
- Halving the target effect approximately quadruples required sample size.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
