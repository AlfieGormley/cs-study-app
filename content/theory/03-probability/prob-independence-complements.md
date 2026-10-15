---
id: prob-independence-complements
title: Test independence and use complements
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Independence is an equality of probabilities.
---

## Independence

A and B are **independent events** if knowing one tells you nothing about the other:

```formula
P(A ∩ B) = P(A) × P(B)
P(A | B) = P(A)   if P(B) > 0
where
P: probability of measurable events, dimensionless and between zero and one
A, B: two events
P(A ∩ B): the probability that both A and B happen
P(A), P(B): the separate probabilities of A and of B
P(A | B): the probability of A given that B happened (| is read "given")
Conditioning: every event to the right of a given bar in this card has positive probability
In words: two events are independent when the chance of both is the product of their chances; equivalently, learning that B happened leaves A's chance unchanged.
```

Independence is a property of the numbers, not of physical separation, and it can be surprising. With two independent fair six-sided dice, "first die is even" and "sum is 7" are independent, but "first die is even" and "sum is 8" are not:

```formula
P(V ∩ S_7) = 3/36 = 1/12
P(V) × P(S_7) = 1/2 × 1/6 = 1/12
P(V ∩ S_8) = 3/36 = 6/72
P(V) × P(S_8) = 1/2 × 5/36 = 5/72
where
V: the event "the first die is even"; P(V) = 1/2
S_7: the event "the sum is 7"; P(S_7) = 6/36 = 1/6
S_8: the event "the sum is 8"; P(S_8) = 5/36
P: probability; probabilities are dimensionless and apply to measurable events
∩: "and", both events together
In words: for "sum is 7" the chance of both equals the product (1/12 each way), so it is independent of the first die being even; for "sum is 8" the two numbers differ (6/72 versus 5/72), so it is not.
```

The intuition: whatever the first die shows, exactly one second-die value makes 7, but a first die of 1 can never make 8.

> [!warning] Disjoint is not independent
> If A and B are disjoint and both have positive probability, they are *dependent*: knowing A happened tells you B certainly did not.

```formula
P(A ∩ B) = 0
P(A) × P(B) > 0
where
P: probability of measurable events, dimensionless and between zero and one
A, B: two disjoint events, each with probability above 0
P(A ∩ B): the probability that both happen, which is 0 because they never happen together
P(A), P(B): their separate probabilities
In words: for disjoint events the chance of both is zero, but the product of their chances is not, so the independence equation fails.
```

## The complement trick

"At least one" questions are almost always easier through the complement. What is the chance of at least one six in four independent rolls of a fair six-sided die?

Counting directly means handling one six, two sixes and so on. Instead, work out the chance of no six at all (each roll avoids a six with probability 5/6, and independent rolls multiply), then subtract from 1.

```formula
P(N = 0) = (5/6)^4 ≈ 0.482
P(N ≥ 1) = 1 − (5/6)^4 ≈ 0.518
where
P: probability of measurable events, dimensionless and between zero and one
N: the number of sixes in the four rolls
P(N = 0): the probability of no six in any of the four rolls
5/6: the chance that one roll is not a six
(5/6)^4: four copies of 5/6 multiplied together, once per independent roll
≈: approximately equal to (rounded)
≥: greater than or equal to
In words: four non-sixes in a row happen about 48% of the time, so at least one six happens about 52% of the time.
```

This is the same calculation as "what is the chance at least one of my 4 requests hits a slow server?" It relies on the rolls (or requests) being independent; correlated failures break the multiplication.

## Key takeaways
- Independence is an equality of probabilities.
- Positive-probability disjoint events are dependent.
- Compute at least one by subtracting the probability of none.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
