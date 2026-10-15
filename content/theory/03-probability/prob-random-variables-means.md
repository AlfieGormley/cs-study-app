---
id: prob-random-variables-means
title: Turn outcomes into random variables and means
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: A random variable is a numerical function of the outcome.
---

Expected-cost analysis asks questions like: how many comparisons does quicksort with uniform random pivots make on average? How many swaps does insertion sort do on a random input? How many servers sit idle if jobs are assigned at random?

Each answer is an **expected value**, and nearly all of them are found with one remarkably powerful tool: **linearity of expectation**. The following units build up to it.

## Random variables

A **random variable** is a measurable function that assigns a number to each outcome of an experiment: events defined by its numerical values must belong to the probability model’s permitted event collection. In the finite examples here, this holds automatically. It is a fixed rule whose value depends on the random outcome; one observed value is a realisation of that rule.

- Roll two dice and map each ordered outcome to its sum; the pair (3, 5) maps to 8.
- Hash a fixed collection of keys into a table and count the collisions.
- Run quicksort on a random permutation and count its comparisons.

The **probability distribution** (or **probability mass function**, PMF) of a discrete random variable lists, for each value it can take, the probability that it takes that value.

```formula
p_X(x) = P(X = x)
where
P: probability of measurable events, dimensionless and between zero and one
X: a discrete random variable, for example the sum of two dice
x: one particular value X might take, for example 8
P(X = x): the probability that X comes out equal to x, from 0 to 1
p_X(x): the probability mass function (PMF) of X evaluated at x; it is the same number, written as a function of x
In words: the PMF is a table giving the chance of every possible value; over all values the chances add up to 1.
```

For the sum of two fair dice, the PMF at 8 is 5/36, because 5 of the 36 ordered pairs sum to 8.

## Expected value

The **expectation** (expected value, or mean) of a random variable is the probability-weighted average of its values: each value counts in proportion to how likely it is. For a discrete variable it is a sum over every value; we need the probability-weighted sum of the absolute values to be finite, so the answer does not depend on the order of adding.

```formula
E[X] = Σ_x x × P(X = x)
where
P: probability of measurable events, dimensionless and between zero and one
E[X]: the expected value of X, the long-run average if the experiment were repeated many times
X: a discrete random variable
x: one of the values X can take
Σ_x: sigma, "add up the following term over every value x"
P(X = x): the probability that X equals x
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: multiply each value by its probability and add the results; likely values pull the average towards themselves.
```

For one fair die, each face has probability 1/6:

```formula
E[X] = (1 + 2 + 3 + 4 + 5 + 6) × 1/6
E[X] = 21/6 = 3.5
where
X: the number shown by one fair six-sided die
E[X]: its expected value
1/6: the probability of each face
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the average roll of a fair die is 3.5.
```

The expected value need not be a possible outcome: you never roll 3.5. For independent, identically distributed repetitions with finite absolute expectation, sample averages converge to it by the **law of large numbers**. Some distributions have no finite expectation.

## Key takeaways
- A random variable is a numerical function of the outcome.
- Its expected value need not be a possible observation.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
