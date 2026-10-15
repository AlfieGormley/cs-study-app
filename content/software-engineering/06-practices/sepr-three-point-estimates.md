---
id: sepr-three-point-estimates
title: Explain a three-point duration estimate
level: intermediate
minutes: 3
summary: Calculate a PERT weighted estimate and make its modelling assumptions explicit.
sourceLesson: sepr-agile-estimation
---

A single date hides the shape of uncertainty. The following illustrative calculation makes one modelling choice visible so stakeholders can question its inputs.

## Ranges and three-point estimates

A single number hides uncertainty. A **three-point estimate** gives three values for one task: an optimistic one, a most likely one and a pessimistic one. **PERT** (the Program Evaluation and Review Technique, developed for the US Navy's Polaris programme in the late 1950s) combines them into a single expected duration by weighting the most likely value four times as heavily as either extreme:

```formula
E = (O + 4 × M + P) / 6
E = (2 d + 4 × 4 d + 12 d) / 6
E = (2 d + 16 d + 12 d) / 6
E = 30 d / 6 = 5 d
where
E: the PERT expected (mean) duration of the task, in days (d)
O: the optimistic estimate, if most things go well, in days; here 2
M: the most likely estimate (the mode), in days; here 4
P: the pessimistic estimate, if most things go badly, in days; here 12
d: days, the unit of time used here
4: the weight given to the most likely value, so it counts four times as much as each extreme
6: the sum of the weights (1 + 4 + 1), which turns the weighted sum back into an average
In words: add the optimistic and pessimistic values to four times the most likely one and divide by six; a long pessimistic tail pulls the expected value above the most likely one.
```

A beta distribution can model durations between chosen optimistic and pessimistic bounds. The PERT weighted mean is an additional modelling assumption, not a consequence of choosing any beta distribution; its parameters must be chosen to give that mean. Under this PERT weighting model the estimated mean (5) is above the mode (4), reflecting the asymmetric inputs. Three inputs alone do not establish the true distribution, and not every duration distribution is right-skewed.

## Key takeaways
- Three-point estimation records optimistic, most likely and pessimistic durations.
- PERT weights the most likely value four times as heavily as either extreme.
- The weighted result is a model estimate, not a deadline or proof of the true duration distribution.

## Further reading
- [PERT in the PMI Practice Standard for Scheduling](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf)
