---
id: prob-ab-experiment-traps
title: Avoid peeking and multiple-testing traps
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: Ordinary fixed-sample tests do not retain error control under arbitrary optional stopping.
---

A small p-value only has its intended meaning under the analysis and sampling plan. Repeated looks, many metrics and broken assignment can undermine a convincing-looking dashboard.

## Stop according to a valid rule

Repeatedly checking an ordinary fixed-sample p-value and stopping at the first crossing can inflate false positives. Cumulative looks reuse data and are dependent, so neither the nominal threshold nor a formula for independent tests gives a universal overall rate.

Choose a sample size and planned analysis, or use a sequential method with error control appropriate to its stopping and sampling rules. Merely counting the number of looks does not specify the error rate.

## Account for multiple opportunities to win

Testing many metrics increases opportunities for false rejection. The precise risk depends on their dependence and individual test error rates. Declare a primary metric in advance and distinguish confirmatory claims from exploration.

The **Bonferroni correction** allocates a family significance budget among the tests and controls the chance of any false rejection without requiring independence. **False discovery rate** control instead targets the expected fraction of false rejections among rejections; procedures such as Benjamini–Hochberg have their own dependence conditions.

## Check the experiment before interpreting treatment

- **Sample ratio mismatch:** an allocation far from the planned split may reveal assignment, eligibility or logging problems. An appropriate allocation test supplies evidence to investigate, not proof of a specific defect.
- **Novelty and learning effects:** a short-lived response to something new may differ from sustained behaviour. Plan duration around relevant cycles; full weeks do not guarantee these effects have settled.
- **Simpson’s paradox:** uneven segment mixtures can reverse an aggregate comparison. Randomisation balances pre-treatment groups in expectation, while attrition and conditioning on post-treatment outcomes can disturb comparisons.
- **Practical significance:** a detectable effect may still be too small to justify its cost. Report effect size and uncertainty.

## Key takeaways
- Repeated stopping opportunities require a suitable analysis.
- Multiple metrics and allocation checks belong in the design.
- A statistical result still needs a practical interpretation.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
