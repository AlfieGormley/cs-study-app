---
id: sepr-three-point-estimates
title: Explain a three-point duration estimate
level: intermediate
minutes: 4
summary: Read a three-point estimate, and why its PERT expected value is a model average, not a safe date.
sourceLesson: sepr-agile-estimation
---

A single number hides how uncertain an estimate is, and in which direction. A three-point estimate makes that visible, and it is worth knowing what its headline figure does and does not mean.

## Ranges and three-point estimates

A **three-point estimate** gives three values for one task: an optimistic one (most things go well), a most likely one, and a pessimistic one (most things go badly). Software tasks are usually lopsided: a 4-day task can easily take 12 days, but it cannot take minus 4.

**PERT** (the Program Evaluation and Review Technique, developed for the US Navy's Polaris programme in 1958) combines the three into one expected duration by weighting the most likely value four times as heavily as either extreme:

```formula reference
E = (O + 4M + P) / 6
where
E: the PERT expected (mean) duration of the task, in days
O: the optimistic estimate, in days
M: the most likely estimate (the mode), in days
P: the pessimistic estimate, in days
4: the weight given to the most likely value
6: the sum of the weights (1 + 4 + 1), which turns the weighted sum back into an average
In words: the expected duration is a weighted mean that counts the most likely value four times and each extreme once, so a long pessimistic tail pulls the expected value above the most likely one.
```

For a task estimated at 2, 4 and 12 days, the PERT expected duration is 5 days: a day above the most likely value, because the slow tail is much longer than the fast one.

## What the number does and does not tell you

The expected duration is an average under a model, not a safe date. PERT is usually paired with a particular beta distribution stretched between the optimistic and pessimistic values. Under that model, for the 2–4–12 task:

- a plan built on the most likely value (4 days) finishes on time only about one time in three;
- a plan built on the PERT expected value (5 days) is only a little better than a coin toss (about 55%);
- about 7 days is needed to finish on time roughly 85% of the time.

Those percentages come from the model, not from the task. The three inputs are themselves guesses, a "pessimistic" guess can still be too optimistic, and the true spread of durations may look nothing like a beta curve. Use the three points to show stakeholders the range and the lopsided risk, and agree which level of confidence a date should carry, rather than quoting a single expected value as a deadline.

## Key takeaways
- Three-point estimation records optimistic, most likely and pessimistic durations.
- PERT weights the most likely value four times as heavily as either extreme.
- Under the usual PERT model, a date set at the expected value is missed almost half the time; quote a range and a confidence level instead.

## Further reading
- [PERT in the PMI Practice Standard for Scheduling](https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf)
- [PERT distribution — Wikipedia](https://en.wikipedia.org/wiki/PERT_distribution)
