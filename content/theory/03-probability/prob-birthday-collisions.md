---
id: prob-birthday-collisions
title: Understand the birthday collision bound
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: The no-collision calculation multiplies successive avoidance probabilities.
---

A collision asks whether any pair matches. That creates far more opportunities than asking whether one new item matches a particular existing item.

## Count opportunities in pairs

Under independent uniform birthdays over 365 days, 23 people already give just over a 50% chance of a shared birthday. The surprise comes from all the pairs in the group, not from filling half the calendar.

To find the exact model probability, consider the complement: every birthday differs. Each new person must avoid all previously used days. Multiply those successive avoidance chances, then subtract from one. The avoidance chance changes as more dates are used.

## How the risk grows

For independent uniform draws from a large space, collisions become likely when the number of draws is around the square root of the space size. Doubling a small population roughly quadruples its pair count and hence its small collision risk.

```formula reference
P(C) ≈ 1 − e^{−(n(n − 1)) / (2m)}
n_{1/2} ≈ √(2 × ln(2) × m)
where
C: the event "at least two draws collide (are equal)"
n: the nonnegative integer number of independent uniform draws (people, IDs, hashes)
m: the positive integer number of equally likely values (365 days, 2^32 IDs, …)
e: Euler's number, about 2.718; each factor 1 − i/m is close to e^{−i/m} when i is small next to m
n_{1/2}: the number of draws at which a collision becomes a 50% chance
ln(2): the natural logarithm of 2, about 0.693
√: the square root
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
In words: Under independent uniform sampling from a large space, collision probability becomes substantial around the square root of the space size.
```

This approximation is useful near the square-root scale for large spaces. Real birthdays need not be independent or uniform; poor random ID generation can similarly concentrate outcomes and increase risk relative to the ideal model.

The expected number of matching pairs and the probability of any match are different. A three-person shared birthday contributes three pairs. An expected pair count can exceed one while a probability cannot.

> [!analogy] Real-world analogy: introductions at a party
> Every new guest can be introduced to everyone already present.
>
> **How it maps:** Each arrival adds several new pairs, just as each new random ID creates collision opportunities with all previous IDs.
>
> **Where it stops:** An introduction is deliberate; a collision occurs only when a pair's independently generated values match under the model.

## Key takeaways
- Any-pair risk grows much faster than one-target risk.
- The complement tracks successive avoidance chances.
- Matching-pair expectation is not a collision probability.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
