---
id: prob-outcomes-events
title: Count outcomes and events
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Count ordered outcomes only when they are equally likely.
---

Probability is the maths of uncertainty. In computer science it turns up everywhere: hash collisions, algorithms using random choices, network packet loss, cache hit ratios, the chance that three replicas fail at once, and every A/B test your product team runs.

These outcomes and events are the foundation for conditional probability, expectations and distributions.

## Sample spaces and events

A **random experiment** is anything with an uncertain outcome: rolling a die, sending a packet, picking a random pivot.

- The **sample space** is the set of all possible outcomes; formulas write it as the Greek capital letter omega. For one die, the sample space is {1, 2, 3, 4, 5, 6}.
- A **random event** (usually just called an event) is a subset of the sample space. "Roll an even number" is the event {2, 4, 6}.
- A **probability** P assigns each event a number between 0 and 1.

In a finite nonempty sample space, when every outcome is equally likely (a fair die, a uniformly random key), probability is just counting: the number of outcomes you are interested in, divided by the number of outcomes there are.

```formula
P(A) = |A| / |Ω|
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the probability of event A, a number from 0 to 1; probability zero need not mean an impossible outcome in an infinite model
A: the event we care about, written as the set of outcomes that count as "A happened"
Ω: omega, the sample space: the set of every possible outcome
|A|: the number of outcomes in A (vertical bars around a set mean "how many elements it has")
|Ω|: the total number of possible outcomes
Conditioning: every event to the right of a given bar in this card has positive probability
In words: when every outcome is equally likely, the probability of an event is the fraction of all outcomes that belong to it.
```

Rolling two independent fair six-sided dice gives 6 × 6 = 36 equally likely ordered pairs. Six of them sum to 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1).

```formula
P(S = 7) = 6 / 36 = 1/6
where
P: probability of measurable events, dimensionless and between zero and one
S: the sum of the two dice, a whole number from 2 to 12
P(S = 7): the probability that the two dice add up to 7
6: the number of ordered pairs that sum to 7
36: the number of ordered pairs (first die, second die), 6 × 6
In words: 6 of the 36 equally likely ordered pairs give a total of 7, so a 7 turns up one roll in six on average.
```

This only works when the outcomes really are equally likely. If they are not (a loaded die, a skewed traffic mix), you must weight each outcome by its own probability instead of counting.

> [!warning] Order matters when counting
> (1,6) and (6,1) are different outcomes. A classic mistake is to treat the 21 unordered pairs as equally likely: that gives the mixed pair {1,6} probability 1/21 instead of 2/36, or gives sum 7 probability 3/21 instead of 6/36. They are not: a double like (3,3) can happen one way, a mixed pair two ways.

## Key takeaways
- Count ordered outcomes only when they are equally likely.
- An event is a set of outcomes; unequal probabilities require weights.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)

> [!note] Evidence gap
> The earlier historical attribution of the four-roll example to a particular 1654 exchange remains omitted because it was not established; the probability calculation is retained in the complement unit.
