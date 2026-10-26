---
id: prob-indicators-fixed-points
title: Count fixed points with indicators
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Each indicator has expectation equal to its event probability.
---

To find an expected count, ask a small yes/no question for each item. An **indicator variable** is one when its event happens and zero otherwise. Its mean is the event's probability.

## Build a count from simple pieces

Give every trial an indicator for success. Adding the indicators gives the total successes. **Linearity of expectation** then adds their probabilities to obtain the expected count, even when the events are dependent.

Ten flips each with marginal head probability 0.3 have expected total three heads. Independence would be needed to call the full count binomial, but is unnecessary for this mean.

## Random returns in a cloakroom

A cloakroom returns a positive number of coats in uniformly random order. Each owner has the same chance of receiving any coat, so their own coat is one possibility among the whole group. Add one match indicator per owner: there is one match on average, regardless of group size.

This is an expectation, not a guarantee of one match in each shuffle. The matches are dependent: if everyone but the final owner receives the correct coat, the final owner must too. That does not invalidate linearity. A match is called a **fixed point** of the permutation.

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

This simulation averages match counts from repeated random shuffles. It should approach one, with variation between runs. The explanation using indicators is what establishes the model expectation.

## Key takeaways
- A count is a sum of yes/no indicators.
- Add individual probabilities to obtain an expected count.
- Dependence affects the distribution without preventing linearity.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
