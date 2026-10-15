---
id: pipe-branch-prediction-counter-state
sourceLesson: pipe-branch-prediction
title: Learn branches with saturating counters
level: intermediate
minutes: 4
summary: Trace one-bit and two-bit predictor state, warm-up, loop exits and predictor aliasing.
---

This unit predicts taken versus not-taken for each observed branch. Taken jumps to a target; not-taken continues sequentially. The counters are teaching models updated after each known Boolean outcome, with no speculative updates or recovery.

## Dynamic prediction: learning from history

### The branch history table

In this simple bimodal model, a **branch history table** (BHT, also called a pattern history table here) is an array indexed by selected bits of the branch’s address (PC). Each counter remembers the outcomes mapped to it. Other predictors index history tables differently, and shared entries need not belong to just one branch.

A **1-bit** entry stores the last outcome and predicts it will happen again. It has a flaw with loops. Consider a loop branch that is taken 9 times and then falls through, with the loop itself run repeatedly:

```
T T T T T T T T T N | T T T ...
                  ^   ^
          mispredict   mispredict again
```

The exit mispredicts, then flips the bit to N, so the first iteration of the *next* run mispredicts too: 2 misses per 10, or 80% accuracy.

### The 2-bit saturating counter

A **2-bit saturating counter** adds hysteresis: a strongly biased state needs two consecutive opposite outcomes to reverse its prediction. From a weak state, one opposite outcome is enough:

```
state  meaning             predict
  3    strongly taken      T
  2    weakly taken        T
  1    weakly not taken    N
  0    strongly not taken  N
```

Taken increments the counter (stopping at 3), not taken decrements it (stopping at 0), and the top bit is the prediction:

```formula
c′ = min(c + 1, 3)   if o = T
c′ = max(c − 1, 0)   if o = N
d = T   if c ≥ 2, else N
where
c: the current state of the counter, a whole number from 0 to 3 (two bits)
c′: the state of the counter after the branch outcome is known
o: the branch's actual outcome
d: the direction the counter predicts before the outcome is known
T: taken: the branch jumps to its target
N: not taken: execution falls through to the next instruction
min: the smaller of the two values, which stops the count at 3
max: the larger of the two values, which stops the count at 0
≥: is greater than or equal to
In words: count up on taken and down on not taken, never leaving 0 to 3, and predict taken whenever the count is in the top half.
```

A single loop exit moves "strongly taken" to "weakly taken", which still predicts taken next time. Now there is only 1 miss per 10.

```python
def two_bit(outcomes, start=1):
    if (type(start) is not int
            or not 0 <= start <= 3):
        raise ValueError("bad start")
    c, miss = start, 0     # 0..3; >=2 = T
    for taken in outcomes:
        # Score before learning the outcome.
        if (c >= 2) != taken:
            miss += 1
        # Saturation keeps c inside 0..3.
        c = min(c + 1, 3) if taken \
            else max(c - 1, 0)
    return miss

def one_bit(outcomes, start=False):
    last, miss = start, 0
    for taken in outcomes:
        if last != taken:
            miss += 1
        # Remember only the latest outcome.
        last = taken
    return miss

# loop branch: taken 9 times, then exits
loop = ([True] * 9 + [False]) * 100
# Miss counts include initial warm-up.
print(one_bit(loop), two_bit(loop))
# 200 101
```

One-bit: 200 misses in 1,000 (80%). Two-bit: 101 (about 90%; the extra 1 is the first warm-up miss).

### Predictor aliasing

The table is indexed by only some PC bits, so two different branches can share an entry and corrupt each other's counters. This is **predictor aliasing**. More capacity can reduce interference. Tags help distinguish entries, but finite capacity and partial tags do not eliminate every collision or replacement effect.

## Key takeaways
- One-bit predictors reverse their guess after one contrary outcome.
- A two-bit counter needs two opposite outcomes to move from a strong prediction to the opposite prediction.
- Initial state and interference matter; the loop accuracy figures state their trace and assumptions.

## Further reading
- [McFarling: Combining Branch Predictors (original report)](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-TN-36.pdf)
- [BOOM implementation: branch prediction](https://docs.boom-core.org/en/latest/sections/branch-prediction/index.html)
