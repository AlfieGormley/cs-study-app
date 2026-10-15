---
id: prob-indicators-fixed-points
title: Count fixed points with indicators
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Each indicator has expectation equal to its event probability.
---

## Indicator variables

An **indicator variable** for an event A is 1 if A happens and 0 otherwise. Its expectation is just a probability:

```formula
E[I_A] = 1 × P(A) + 0 × P(¬A)
E[I_A] = P(A)
where
P: probability of measurable events, dimensionless and between zero and one
A: an event
I_A: the indicator of A: 1 if A happens, 0 if not
E[I_A]: its expected value
P(A): the probability of A
¬A: "not A", the event that A does not happen (¬ is "not")
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the average of a 0-or-1 switch is just the chance it is on.
```

The recipe for "expected number of things that happen" is:

1. Write the count as a sum of indicators, one per thing.
2. Find each indicator's probability.
3. Add them up, by linearity.

## Example: fixed points of a random permutation

A positive number of people check their hats; the hats are handed back in a uniformly random order. How many people expect to get their own hat? A person who gets their own hat back is a **fixed point** of the shuffle.

Each person's own hat is just one of all the equally likely hats they could receive. Its match probability is therefore one divided by the number of people.

```formula
F = I_1 + I_2 + … + I_n
E[F] = Σ_i E[I_i] = n × (1/n) = 1
where
F: the number of people who get their own hat back (fixed points)
n: the positive integer number of people; the permutation is uniform
I_i: the indicator that person i gets their own hat: 1 if so, 0 if not
I_1, I_2, I_n: the indicators for person 1, person 2 and the last person, n
i: a counter running over the people, 1 to n
E[ ]: expected value
Σ_i: sigma, "add up over every person i"
…: and so on, one indicator per person
1/n: the chance a given person gets their own hat
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: n people each with a 1-in-n chance gives an expected total of exactly 1.
```

The answer is 1 for every positive n, whether 3 people or 3 million. With two or more people the indicators are dependent (if all but one have their own hats, the last must too), but linearity does not care.

## Checking by simulation

```python
import random

def fixed_points(n):
    p = list(range(n))
    # Assign each owner a shuffled item.
    random.shuffle(p)
    return sum(p[i] == i for i in range(n))

t = 100_000
print(sum(fixed_points(50)
          for _ in range(t)) / t)  # ~1.0
```

## Key takeaways
- Each indicator has expectation equal to its event probability.
- Dependent coat-return events still have an expected total of one.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
