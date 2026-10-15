---
id: prob-positive-test-counts
title: Interpret a positive test using counts
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Sensitivity is not the chance of illness after a positive result.
---

## The classic test example

In a hypothetical probability model, a condition affects 1% of people and a test has:

- **Sensitivity** (true positive rate) 99%: an ill person tests positive 99% of the time.
- **False positive rate** 5%: a healthy person tests positive 5% of the time (so the **specificity**, the chance a healthy person tests negative, is 95%).

You test positive. What is the chance you are ill?

```formula
P(T) = P(T | I) × P(I) + P(T | ¬I) × P(¬I)
P(T) = 0.99 × 0.01 + 0.05 × 0.99
P(T) = 0.0099 + 0.0495 = 0.0594
P(I | T) = (P(T | I)P(I)) / P(T)
P(I | T) = 0.0099 / 0.0594 ≈ 0.167
where
I: the event "the person is ill"; the prior P(I) = 0.01 (1% prevalence)
¬I: "not ill", healthy; P(¬I) = 0.99
T: the event "the test is positive"
P: probability; probabilities are dimensionless and apply to measurable events
|: read "given"
P(T | I): the sensitivity, 0.99
P(T | ¬I): the false positive rate, 0.05
P(I | T): the posterior, the chance of being ill given a positive test
≈: approximately equal to
Conditioning: every event to the right of a given bar in this card has positive probability
In words: positives come from 0.99% of people who are ill and 4.95% of people who are healthy, so only about one positive in six is ill.
```

Only about **1 in 6** positives is genuinely ill, despite 99% sensitivity. Sensitivity and overall accuracy are different quantities.

## Natural frequencies make it obvious

Use expected counts in a hypothetical group of 10,000 people:

```
          10,000 people
         /             \
    100 ill          9,900 healthy
    /     \           /         \
 99 +     1 -     495 +      9,405 -

```

The positives are 99 + 495 = 594 people, and 99 of them are ill:

```formula
P(I | T) = N_TP / (N_TP + N_FP)
P(I | T) = 99 / (99 + 495) = 99 / 594
P(I | T) ≈ 0.167 = 16.7%
where
N_TP: the expected number of **true positives**, ill people who test positive: 99 % of 100 = 99
N_FP: the expected number of **false positives**, healthy people who test positive: 5 % of 9,900 = 495
P(I | T): the chance a person is ill given a positive test (| is read "given")
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
%: per cent, hundredths; 16.7% = 0.167
Conditioning: every event to the right of a given bar in this card has positive probability
In words: of the 594 people who test positive, 99 are really ill, about one in six.
```

The 495 false positives swamp the 99 true positives because the healthy group is 99 times larger. The table of counts makes the numerator and denominator explicit; its entries are expected counts, not guaranteed outcomes in every sample.

> [!note] Evidence gap
> The previous broad claim about how much better people reason with counts is omitted here because its study populations, tasks and effect sizes were not established in this review. No population-wide claim is needed for the arithmetic.

## Key takeaways
- Sensitivity is not the chance of illness after a positive result.
- Expected true and false positives give the posterior denominator.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
