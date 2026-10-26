---
id: prob-simulation-enumeration
title: Check a model by simulation and enumeration
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Enumeration is exact for finite equally likely outcomes.
---

A simulation samples outcomes from a model; enumeration lists every outcome. Both can catch reasoning errors, but neither establishes that the model represents the real system.

## Sample a model

The code models independent fair die rolls and records whether any of four rolls is a six. Each experiment produces one yes/no observation.

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

The printed fraction varies between runs. With independent identically distributed experiments it approaches the model probability as the sample grows, but it need not move closer after every extra trial.

## Enumerate when the space is small

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

Here every ordered dice pair is equally likely. Filtering to the known total changes the denominator as well as the numerator. The fraction is exact for this model because every permitted outcome is included, rather than sampled.

## Choose an appropriate check

Enumeration becomes expensive as the outcome space grows. Simulation scales more readily, but rare events may be missed entirely in a finite run. Seeing no failures is not proof that their probability is zero.

The **standard error** describes variation between estimates. For independent yes/no trials, increasing the trial count fourfold halves the standard error; it does not guarantee a particular realised error. Small relative errors for rare probabilities can require many trials.

If real retries share an outage while the simulation gives each an independent fresh chance, more simulation only estimates the wrong model more precisely. Test the assumptions against observations too.

## Key takeaways
- Enumeration is exact when the outcomes and weights are fully specified.
- Simulation estimates a model probability with sampling variation.
- Rare events and incorrect assumptions need special care.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
