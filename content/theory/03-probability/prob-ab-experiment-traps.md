---
id: prob-ab-experiment-traps
title: Avoid peeking and multiple-testing traps
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: Ordinary fixed-sample tests do not retain error control under arbitrary optional stopping.
---

## How A/B tests go wrong

## Peeking

Checking the p-value every day and stopping as soon as it dips below 0.05 can inflate the false positive rate above the stated 5%. Each look is another chance for noise to cross the line. The amount of inflation depends on the test, sample sizes, look schedule and stopping rule.

> [!note] Evidence gap
> The previous 19% false-positive figure and claimed simulation run are omitted because no reproducible simulation or adequately specified design supported them. Ten looks do not determine one universal error rate.

Fixes: fix the sample size in advance and look once; or use methods designed for continuous monitoring (sequential testing, always-valid p-values), with error control appropriate to the sampling and stopping rules.

## Multiple comparisons

For 20 independent tests, each with exact null rejection probability 0.05, the chance of at least one false rejection is:

```formula
P(F) = 1 − (1 − α)^k
P(F) = 1 − 0.95^20 ≈ 0.64
where
F: the event "at least one test is falsely declared significant"
α: alpha, each test's false positive rate, 0.05
k: the number of independent tests, 20
0.95^20: the chance all 20 correctly come out non-significant
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
In words: twenty independent 5% chances add up to about a 64% chance of at least one false alarm.
```

A false rejection is likely in this independent example, but not certain. Correlated metrics need not have this 64% probability. Declare one primary metric in advance, and correct for multiple tests (the **Bonferroni correction** tests each metric at the family significance level divided by the number of metrics, so 0.05 / 20 = 0.0025; or control a different quantity, the false discovery rate, with Benjamini–Hochberg under its independence or appropriate positive-dependence assumptions). Bonferroni controls family-wise error without requiring independence.

## Other traps

- **Sample ratio mismatch (SRM).** You planned a 50/50 split but got 50.8/49.2 on a million users. A **chi-squared test** shows this is wildly unlikely by chance, so investigate assignment and logging (for example redirects, bot filters or crashes) before interpreting the treatment comparison; this is strong evidence of a mismatch, not logical proof of a particular defect.
- **Novelty and learning effects.** Users click a new button because it is new. Use a pre-planned duration that covers relevant cycles; full weeks can address weekly seasonality but do not guarantee novelty or learning effects have settled.
- **Simpson's paradox.** A variant can win in every segment yet lose overall (or vice versa) if the segments are unevenly mixed between arms. Randomisation balances pre-treatment groups in expectation, but finite-sample imbalance, attrition or post-treatment conditioning can still produce this pattern. The issue also affects observational comparisons such as "users who enabled feature X convert more".
- **Statistical versus practical significance.** With enough data, a small effect can be statistically significant and still not justify the implementation cost. Whether a particular lift is detectable depends on its units, baseline variance and design. Always report the effect size with a confidence interval, not just p.

## Key takeaways
- Ordinary fixed-sample tests do not retain error control under arbitrary optional stopping.
- Multiple-testing corrections and allocation checks precede treatment interpretation.
- Statistical significance alone does not establish practical value.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
