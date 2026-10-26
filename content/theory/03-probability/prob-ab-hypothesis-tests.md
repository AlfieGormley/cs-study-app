---
id: prob-ab-hypothesis-tests
title: Interpret an A/B hypothesis test
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: A p-value conditions on the null model rather than assigning it a posterior probability.
---

An **A/B test** randomly assigns users to control and variant groups and compares a chosen metric. Randomisation balances other factors in expectation, not perfectly in every realised experiment.

## Ask what the null model predicts

The **null hypothesis** commonly says the variant has no effect. A test statistic measures the observed discrepancy from that model. A **p-value** is the probability, assuming the null and sampling model, of a statistic at least as extreme in the pre-specified direction or directions.

A pre-planned one-sided p-value of 0.03 means such an extreme result would occur about 3% of the time under the null model. It does not mean a 3% probability that the null is true, a 97% probability the variant helps, or a 3% effect size.

## Distinguish decisions from truth

A significance level is a planned bound on false rejection under the test assumptions. A significant result can be a **Type I error**: rejecting a true null. Failing to reject when a real effect exists is a **Type II error**. **Power** is the chance of rejecting under a specified real effect.

Actual error rates depend on the procedure and assumptions. Discrete tests can be conservative; approximations can be inaccurate. Report the effect estimate and uncertainty as well as significance.

## Interpret an inconclusive result

Suppose a planned two-sided test reports a p-value of 0.058 against a 0.05 threshold. It has not met that rule for rejecting the null. That does not establish no effect: the data may be too noisy for the effect size of interest.

Do not keep extending an ordinary fixed-sample test until it crosses the threshold. Use the planned design or an appropriate sequential procedure. Likewise, a statistically significant tiny change may still be too small to justify implementation costs.

## Key takeaways
- P-values condition on a null model; they do not assign it a posterior probability.
- Failure to reject is not proof of no effect.
- Power, effect size and practical value remain separate questions.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
