---
id: prob-alert-base-rates
title: Interpret rare-event alerts
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Precision depends on prevalence as well as conditional detection rates.
---

An alert queue can be mostly false alarms even when a detector catches nearly every real problem. Whether this happens depends on the base rate and false-positive rate together.

## Measure the decision you actually face

**Classifier recall** (usually shortened to recall) or sensitivity is the share of real cases detected. **Classifier precision** (usually shortened to precision) is the share of alerts that are real. **Classification accuracy** is the share of all predictions that are correct. On strongly imbalanced data, always predicting the common class can achieve high accuracy while finding none of the rare cases.

A fraud team deciding which alerts to investigate needs precision as well as sensitivity. A rare cause creates many more opportunities for false alerts than true ones, so a small false-positive rate may dominate the queue. Rarity alone does not imply poor precision: a detector with no false positives is a counterexample.

## Compare changes under explicit assumptions

When true and false alerts both occur, holding sensitivity and prevalence fixed while reducing false positives improves precision. Holding positive sensitivity and a positive false-positive rate fixed, increasing prevalence within a mixed population also improves precision. With no false positives, precision is already perfect whenever alerts occur. If sensitivity is already near perfect and false alerts dominate, a tiny sensitivity improvement has little effect on queue quality.

Real threshold changes often trade sensitivity against false positives. A filter selecting a higher-risk population can change both conditional rates. Re-estimate them in that population instead of assuming only the prevalence changed.

Daily true and false alert counts predicted by a model are expectations, not a promise for every day's queue. Combine rate measurements with investigation costs and the consequences of missed cases.

## Key takeaways
- Detection rate, precision and accuracy answer different questions.
- Base rates matter even when detector rates are known precisely.
- Re-estimate rates after a threshold or population change.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
