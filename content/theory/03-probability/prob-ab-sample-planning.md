---
id: prob-ab-sample-planning
title: Plan an A/B sample size
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: Choose effect size, significance and power before collecting the sample.
---

Before collecting an A/B sample, decide how small an effect matters. A study can be large enough to detect a major change yet too noisy to resolve a smaller one.

## Specify the design inputs

Choose the primary metric, expected baseline rate, minimum detectable effect, significance level, desired power and allocation between arms. For a conversion rate, distinguish percentage points from relative change: moving from 10% to 11% is one percentage point and a 10% relative increase.

Power is the chance the planned test detects a specified real effect under the model. An 80% target is a design choice, not a promise that the experiment will show significance or that a significant result is 80% likely to be real.

## Small effects require much more data

At similar variance and fixed significance and power, halving the target effect approximately quadruples the required sample. Sampling noise shrinks with the square root of sample size, so reducing that noise by half takes about four times the data.

The following approximation is a reference for equal-sized independent conversion-rate arms near a shared baseline, two-sided 5% significance and 80% power:

```formula reference
n ≈ (16p(1 − p)) / δ^2
where
n: users per arm
p: the baseline conversion probability, strictly between zero and one
δ: delta, the positive absolute probability difference to detect, not a relative percentage change
16: about 2 × (1.96 + 0.84)^2 = 15.7, rounded up; it bakes in 5% significance and 80% power
≈: approximately equal to
In words: For this approximate equal-arm design, required users per arm grow with outcome variance and with the inverse square of the target absolute difference.
```

Use an appropriate planning method for the actual test, baseline and allocation. This shortcut is not an exact power guarantee, especially with rare outcomes or small samples.

## Plan a feasible experiment

Translate users per arm into duration at available traffic, allowing for the intended sampling unit and relevant cycles. If the needed sample exceeds a stable experiment window, reconsider the detectable effect or design. Reading a visible trend does not create missing information.

Pre-specify the stopping plan. A valid sequential design can use a different stopping rule, but repeatedly extending an ordinary fixed-sample test changes its error properties.

## Key takeaways
- Plan around an effect that matters, stated in clear units.
- Smaller effects usually require much larger samples.
- Sample-size approximations and stopping rules depend on the design.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
