---
id: prob-geometric-memoryless
title: Model geometric waits and memorylessness
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: The geometric distribution counts through the first success.
---

## Geometric: how long until the first success?

Repeat independent Bernoulli trials, each succeeding with the same probability, until the first success. The number of trials has a **geometric distribution**:

```formula
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
In words: fail k − 1 times then succeed once; on average it takes 1/p tries, and the chance of a long wait shrinks by a factor of 1 − p per extra try.
```

If every attempt succeeds with probability one, the first attempt is always the successful one. Treat that deterministic endpoint separately rather than evaluating a zero-to-zero power in the mass formula.

For a retry that succeeds 20% of the time, the mean is 5 attempts, and the chance of still failing after 10 attempts is 0.8¹⁰ ≈ 0.107.

Independent retries with constant success probability and independent fair-die rolls until a six fit this model. Open-addressing probes generally are not independent draws with replacement, so geometric waiting time is only a simplified probing model, not an exact law for every table.

## Memorylessness

The geometric distribution is **memoryless**: having already waited tells you nothing about how much longer you will wait.

```formula
P(T > m + k | T > m) = P(T > k)
where
T: the number of trials until the first success
m: the number of trials that have already failed; a whole number 0 or more
k: how many more trials we ask about; a whole number 0 or more
P(T > m): the probability of failing the first m trials; must be above 0
|: read "given"; the left side assumes the first m trials failed
P: probability; probabilities are dimensionless and apply to measurable events
Conditioning: every event to the right of a given bar in this card has positive probability
In words: after m failures, the chance of needing more than k further trials is exactly what it was at the start.
```

If the success probability p is strictly between 0 and 1 and you have already failed 10 times, the expected number of further attempts is still the reciprocal of the success probability. The past failures are sunk; they do not make success "due". This is the formal version of the gambler's fallacy, and it holds only when trials really are independent with constant success probability. Persistent server overload can correlate failures or change the success probability; backoff can reduce retry load in that setting.

## Key takeaways
- The geometric distribution counts through the first success.
- Past failures change nothing only under independent constant-probability trials.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
