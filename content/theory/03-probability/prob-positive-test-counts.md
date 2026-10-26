---
id: prob-positive-test-counts
title: Interpret a positive test using counts
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Sensitivity is not the chance of illness after a positive result.
---

Use counts to see which group a test result refers to. This is a hypothetical probability model, not an assessment of an individual medical result.

## Start from the whole population

Suppose a condition affects 1% of a population. A test detects 99% of affected people: its **sensitivity**. It also flags 5% of unaffected people: its **false positive rate**. Its **specificity**, the proportion of unaffected people testing negative, is 95%.

The expected counts in a hypothetical group of 10,000 are:

| Group | Expected positive | Expected negative |
|---|---|---|
| 100 affected | 99 | 1 |
| 9,900 unaffected | 495 | 9,405 |

These are model expectations; an actual group need not contain precisely these counts.

## Now restrict attention to positive results

Among the 594 expected positives, only 99 are affected: about one in six. The many unaffected people produce more false positives even though each has a relatively small chance of testing positive.

Sensitivity asks about results among affected people. **Positive predictive value**, also called precision, asks about affected people among positive results. Specificity asks about negative results among unaffected people. Changing the denominator changes the question.

The positive result still provides evidence: the model probability rises above the original 1%. “Most positives are false” does not mean the test tells us nothing. Its interpretation depends on prevalence and both conditional test rates.

## Key takeaways
- Keep the reference group explicit when interpreting a percentage.
- Compare expected true and false positives within the positive group.
- Expected counts explain the model, not guaranteed individual outcomes.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
