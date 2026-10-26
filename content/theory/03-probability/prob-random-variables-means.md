---
id: prob-random-variables-means
title: Turn outcomes into random variables and means
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: A random variable is a numerical function of the outcome.
---

A **random variable** is a rule that assigns a number to an outcome. The rule is fixed; the outcome is uncertain. Rolling two dice and recording their sum is one rule, while recording whether they match is another.

## Separate outcomes from measurements

A **probability distribution** describes how likely the numerical values are. For a discrete variable, its **probability mass function** gives the probability of each value. In general models the rule must be measurable: events described by its values must belong to the model's permitted collection of events. Finite examples satisfy this automatically.

Counting comparisons in a randomised sort, idle servers after random assignment or bytes transferred all turns uncertain behaviour into numerical quantities we can analyse.

## What a mean predicts

The **expected value** is the probability-weighted average: common values contribute more than rare values. For a discrete finite-mean model, sum each value times its probability. A finite absolute expectation ensures the result is independent of summation order.

```formula reference
E[X] = Σ_x x × P(X = x)
where
P: probability of measurable events, dimensionless and between zero and one
E[X]: the expected value of X, the long-run average if the experiment were repeated many times
X: a discrete random variable
x: one of the values X can take
Σ_x: sigma, "add up the following term over every value x"
P(X = x): the probability that X equals x
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: Expectation is the probability-weighted average of possible numerical values, when the finite absolute expectation exists.
```

A fair six-sided die has expected value 3.5 even though no roll shows 3.5. The mean describes averaging across repetitions, not a promised or most likely individual outcome.

Under independent identically distributed repetitions with finite absolute expectation, sample averages converge to the expectation by the **law of large numbers**. This does not guarantee that each additional observation improves an estimate. Some distributions have no finite expectation, so check that the mean being discussed exists.

## Key takeaways
- A random variable numerically describes an uncertain outcome.
- Expectation weights values by their probabilities.
- The mean need not be an observable value or a single-run prediction.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
