---
id: prob-birthday-collisions
title: Derive the birthday collision bound
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: The no-collision calculation multiplies successive avoidance probabilities.
---

## The birthday problem

How many people must be in a room before two probably share a birthday? Under independent uniform birthdays over 365 days, the first group size with a collision probability above 50% is **23**.

Each new person must avoid the birthdays of all the earlier ones. Multiply those chances:

```formula
P(U) = 365/365 × 364/365 × …
  × (365 − n + 1)/365
P(U) ≈ 0.493   for n = 23
P(¬U) ≈ 1 − 0.493 = 0.507
where
U: the event "all n people have different birthdays"
¬U: "not U", at least two people share a birthday
n: the integer number of people in the room, from 1 through 365 for this product; above 365, a match is certain
365: the number of equally likely birthdays (ignoring 29 February)
(365 − n + 1)/365: the chance the n-th person avoids the n − 1 birthdays already taken
…: and so on, one factor per person
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
In words: with 23 people, the chance everyone's birthday is different has already dropped below a half.
```

The reason it is so low: what matters is the number of **pairs**, and 23 people form 23 × 22 / 2 = 253 pairs, each of which might match.

## The birthday bound

For independent uniform draws from a large space, the no-collision product can be approximated with the natural exponential. Setting the result to one half gives the **birthday bound**:

```formula
P(C) ≈ 1 − e^{−(n(n − 1)) / (2m)}
n_{1/2} ≈ √(2 × ln(2) × m)
n_{1/2} ≈ 1.18 × √(m)
where
C: the event "at least two draws collide (are equal)"
n: the nonnegative integer number of independent uniform draws (people, IDs, hashes)
m: the positive integer number of equally likely values (365 days, 2^32 IDs, …)
e: Euler's number, about 2.718; each factor 1 − i/m is close to e^{−i/m} when i is small next to m
n_{1/2}: the number of draws at which a collision becomes a 50% chance
ln(2): the natural logarithm of 2, about 0.693
1.18: √(2 × ln(2)) ≈ 1.1774
√: the square root
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
In words: collisions become a coin flip at about 1.18 times the square root of the number of possible values.
```

The approximation is accurate when the number of draws is comparable to the square root of a large space size. Applying the threshold approximation to 365 days gives about 22.5 people, close to the exact threshold of 23.

Collisions become likely at about the **square root** of the space size, not at the space size.

```python
def p_collision(n, m):
    if (not isinstance(n, int)
            or not isinstance(m, int)
            or n < 0 or m < 1):
        raise ValueError("invalid n or m")
    # Too many draws force a repeat.
    if n > m:
        return 1.0
    # Multiply the avoidance chances.
    p_unique = 1.0
    for i in range(n):
        p_unique *= (m - i) / m
    return 1 - p_unique

print(round(p_collision(23, 365), 3))
# 0.507
```

## Key takeaways
- The no-collision calculation multiplies successive avoidance probabilities.
- The number of pairs makes collisions likely at the square root of the space size.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
