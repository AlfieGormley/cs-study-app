---
id: prob-simulation-enumeration
title: Check a model by simulation and enumeration
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Enumeration is exact for finite equally likely outcomes.
---

## Checking your answers by simulation

When you are unsure of a calculation, simulate it. For independent trials from the specified model, the sample frequency converges to the model probability as the number of trials grows. This checks arithmetic against a simulation; it does not establish that the model describes the real system.

```python
import random

def at_least_one_six(rolls=4):
    # Stop as soon as one roll is a six.
    return any(random.randint(1, 6) == 6
               for _ in range(rolls))

trials = 1_000_000
# Count successful simulated experiments.
hits = sum(at_least_one_six()
           for _ in range(trials))
print(hits / trials)   # about 0.518
```

For small sample spaces you can be exact instead, by enumerating every outcome:

```python
from itertools import product
from fractions import Fraction

dice = list(product(range(1, 7), repeat=2))
# Restrict the space to the known sum.
sum8 = [d for d in dice if sum(d) == 8]
# Count favourable outcomes within it.
first3 = [d for d in sum8 if d[0] == 3]
print(Fraction(len(first3), len(sum8)))
# 1/5
```

How close should the simulated fraction be? Each simulated run is a **Bernoulli trial** (a yes/no experiment), and the typical size of the error in the estimated fraction is its **standard error**:

```formula
SE = √((p(1 − p)) / n)
SE ≤ √(0.25 / 1,000,000) = 0.0005
where
SE: the standard error, the typical distance between the simulated fraction and the true probability
p: the true probability being estimated (about 0.518 here)
n: the number of independent simulated trials, here 1,000,000
√: the square root
≤: less than or equal to
0.25: the largest possible value of p × (1 − p), reached when p = 0.5
In words: the error shrinks like one over the square root of the number of trials, so a million trials gives a typical error of at most 0.0005.
```

This is not a guarantee of three correct decimal places: the estimate can stray a few standard errors. Rare events (tiny p) can require far more trials for small relative error; exact enumeration is preferable when feasible.

## Common pitfalls

- **Assuming equal likelihood.** Counting outcomes only works if each is equally likely. "Either it rains or it doesn't" is not 50/50.
- **Confusing "A given B" with "B given A".** The chance a test is positive given disease is not the chance of disease given a positive test. The next lesson is entirely about this.
- **Assuming independence by default.** Retries to the same overloaded server, disks from the same batch, and users in the same household can be correlated.
- **The gambler's fallacy.** Independent events have no memory. After five heads, a fair coin is still 50/50.

## Key takeaways
- Enumeration is exact for finite equally likely outcomes.
- Simulation checks a model; it does not establish that real failures follow it.
- Standard error describes variability rather than a guaranteed error limit.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
