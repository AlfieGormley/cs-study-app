---
id: prob-odds-repeated-evidence
title: Update odds and repeated evidence
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Likelihood ratios multiply prior odds.
---

**Odds** compare the chance a hypothesis is true with the chance it is false. A 1% probability is odds of one to 99. Probability and odds express the same belief on different scales.

## Evidence multiplies odds

A **likelihood ratio** compares how likely the observed evidence is under the hypothesis and under its alternative. Evidence more likely under the hypothesis raises its odds; equally likely evidence leaves them unchanged; evidence more likely under the alternative lowers them.

```formula reference
O_post = O_prior × L_ratio
L_ratio = P(E | H) / P(E | ¬H)
where
O_prior: the odds of H before the evidence
O_post: the odds of H after the evidence
L_ratio: the likelihood ratio
H: the hypothesis; ¬H means "H is false" (¬ is "not")
E: the evidence
P(E | H): how likely the evidence is if H is true (| is read "given")
P(E | ¬H): how likely the evidence is if H is false; must be above 0
P: probability; probabilities are dimensionless and apply to measurable events
In words: multiply the prior odds by the evidence's likelihood under the hypothesis divided by its likelihood under the alternative.
```

The displayed ratio assumes both hypotheses have positive priors and the evidence has positive probability under the alternative. Multiplying odds is different from multiplying probability. Strong evidence can favour a rare hypothesis without making it the most likely explanation.

## Do repeated results add new information?

After an update, use the posterior as the prior for the next piece of evidence. Conditional independence both when the hypothesis is true and when it is false is sufficient to multiply the individual likelihood ratios unchanged. Without it, calculate each new likelihood ratio conditional on the evidence already seen; do not assume the original ratio still applies.

Copying an alert into a second dashboard does not create a second independent observation. Two tests sharing the same faulty input may repeat the same error. Use the likelihood of the new evidence given what is already known; do not blindly multiply an unchanged ratio again.

Under genuine conditional independence, requiring two positive detectors reduces false positives by requiring both to fire, but also misses real cases whenever either fails to detect them. Improved precision can come at a sensitivity cost.

## Key takeaways
- Likelihood ratios change odds, not probabilities directly.
- Sequential updates must account for previous evidence.
- Conditional independence in both classes permits multiplying the individual likelihood ratios unchanged.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
