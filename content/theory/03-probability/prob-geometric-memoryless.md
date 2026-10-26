---
id: prob-geometric-memoryless
title: Model geometric waits and memorylessness
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: The geometric distribution counts through the first success.
---

A **geometric distribution** models the number of independent constant-probability trials up to and including the first success. It answers a waiting question, not a count within a fixed batch.

## A run of failures does not make success due

When the success probability is strictly between zero and one and attempts are independent, knowing that several attempts failed leaves the future trial distribution unchanged. The remaining wait has the same distribution as the original wait. This is **memorylessness**.

The expected further wait is therefore unchanged after any possible failure streak. Total attempts so far still increase: memorylessness concerns what remains, not erasing the cost already paid. A long wait remains possible even when the expected wait is short.

```formula reference
P(T = k) = (1 − p)^{k − 1} × p
E[T] = 1 / p
Var(T) = (1 − p) / p^2
P(T > k) = (1 − p)^k
where
P: probability of measurable events, dimensionless and between zero and one
T: the number of trials up to and including the first success
k: a particular trial count, 1, 2, 3, …
p: the fixed success probability, strictly between 0 and 1 for the displayed mass formula; success probability one is the deterministic case described below
(1 − p)^{k − 1}: the chance the first k − 1 trials all fail
P(T = k): the probability that the first success is on trial k
E[T]: the expected number of trials
Var(T): the variance of the number of trials
p^2: p multiplied by itself
P(T > k): the probability of still having no success after k trials
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: a first success on a chosen attempt requires every earlier attempt to fail. The mean wait is the reciprocal of the success chance; each extra failure multiplies the remaining tail probability by the fixed failure chance.
```

At success probability one, the first attempt succeeds with certainty. A failure streak is then impossible and cannot be used as an ordinary conditioning event. Success probability zero gives no eventual success and falls outside this proper geometric model.

## Check whether the real process remembers

After several failed requests, a persistent outage may be more plausible than it was before. That is evidence against treating every attempt as an independent draw with a fixed success chance. Retries can also add load and change the chance of recovery.

Backoff can reduce retry pressure, but its effect requires a system model. Open-addressing hash probes also generally do not behave like independent draws with replacement, so a geometric model is a simplification rather than a universal probing law.

## Key takeaways
- Memorylessness describes the remaining wait under specific assumptions.
- Past effort does not make success due in an independent fixed-probability model.
- Persistent causes or changing conditions invalidate that simple interpretation.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
