---
id: prob-geometric-mean
title: Derive the expected wait for success
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Independent constant-probability attempts restart after a failure.
---

## Waiting for success: the geometric case

A request succeeds with the same probability p (more than 0, at most 1) on each independent attempt. How many attempts does it take on average? The number of attempts T has a **geometric distribution**, and:

```formula
E[T] = 1 / p
E[T] = 1 / 0.2 = 5
where
T: the number of attempts up to and including the first success
E[T]: the expected (long-run average) number of attempts
p: the probability that one attempt succeeds; 0.2 (20%) in the second line
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: if each try succeeds one time in five, you need five tries on average.
```

A neat derivation: with probability p you finish after 1 attempt; otherwise you have used 1 attempt and are back where you started, because independent attempts have no memory.

```formula
E[T] = 1 + (1 − p) × E[T]
p × E[T] = 1
E[T] = 1 / p
where
E[T]: the expected number of attempts
1: the attempt you always make
p: the chance that attempt succeeds
1 − p: the chance it fails, after which you face the same problem again
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: one attempt, plus (if it failed) a fresh copy of the whole wait; solving for the expected wait gives 1/p.
```

The restart equation identifies a finite mean; finiteness must not simply be assumed. Summing the geometric tail probabilities gives a convergent geometric series because the failure probability is strictly below one. This supplies the finite-expectation justification for the rearrangement.

## Key takeaways
- Independent constant-probability attempts restart after a failure.
- Count the successful attempt as part of the waiting time.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
