---
id: prob-total-probability
title: Weight cases with total probability
level: basic
minutes: 3
sourceLesson: prob-basics
summary: A partition covers every outcome exactly once.
---

## The law of total probability

For a countable partition of the sample space into disjoint pieces (every outcome lies in exactly one piece), find an event's overall chance by working out its chance inside each piece and weighting by how likely each piece is. Pieces with zero probability are left out.

```formula
P(A) = Σ_i P(A | B_i) × P(B_i)
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the overall probability of event A
B_i: the i-th piece of the partition, for example "the request went to region i"
i: an index counting the pieces 1, 2, 3, …
Σ_i: sigma, "add up the following term for every piece i"
P(A | B_i): the probability of A given that we are in piece B_i (| is read "given")
P(B_i): the probability of landing in piece B_i
Conditioning: every event to the right of a given bar in this card has positive probability
In words: the overall chance of A is a weighted average of its chance in each case, weighted by how often each case happens.
```

Suppose 70% of your traffic hits region X with a 1% error rate and 30% hits region Y with a 4% error rate.

```formula
P(R) = P(R | X) × P(X) + P(R | Y) × P(Y)
P(R) = 0.01 × 0.7 + 0.04 × 0.3
P(R) = 0.007 + 0.012 = 0.019
where
P: probability of measurable events, dimensionless and between zero and one
R: the event "a request returns an error"
X: the event "the request went to region X"; P(X) = 0.7 (70%)
Y: the event "the request went to region Y"; P(Y) = 0.3 (30%)
P(R | X): the error rate given region X, 0.01 (1%); | is read "given"
P(R | Y): the error rate given region Y, 0.04 (4%)
Conditioning: every event to the right of a given bar in this card has positive probability
In words: the overall error rate is 1.9%, a traffic-weighted average of the two regional rates.
```

This rule supplies the evidence denominator in the later Bayesian update.

## A host policy changes the weights

A car is uniformly hidden behind three doors. You pick door 1. A host who knows the hiding place always opens an unpicked goat door and offers a switch. If both goat doors are available, the host chooses each with equal probability. Let the observation be that door 3 was opened. Partition by the car location: the observation has probability one-half with the car at door 1, one with it at door 2, and zero with it at door 3.

```formula
P(H_3) = (1/2)(1/3) + 1(1/3)
P(H_3) = 1/2
P(C_2 ∩ H_3) = 1/3
P(C_2 | H_3) = (1/3) / (1/2) = 2/3
where
C_2: the event that the car is behind door 2
H_3: the event that the host opens door 3
P: probability in this three-door model; probabilities are dimensionless and apply to measurable events
∩: intersection, both events happen
|: given the event to the right; the denominator here is positive
Conditioning: every event to the right of a given bar in this card has positive probability
In words: weight the host observation by each possible car location, then divide the joint chance by the chance of the observation; switching wins with probability two-thirds.
```

The host policy is part of the experiment. Opening an unpicked door at random, without knowing where the car is, and happening to show a goat would produce a different conditional probability.

## Key takeaways
- A partition covers every outcome exactly once.
- Weight conditional probabilities by the chance of each case.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
