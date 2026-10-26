---
id: prob-binomial-counts
title: Model fixed trials with the binomial
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: A binomial count needs independent trials with one fixed probability.
---

A distribution is useful when its assumptions describe the process. Start by asking what you count and when you stop, rather than choosing a familiar formula.

## Fixed trials, count the successes

A **Bernoulli trial** has two outcomes, conventionally called success and failure. “Success” is just the counted outcome: a failed disk can be a success for a failure-count model.

A **binomial distribution** counts successes in a fixed number of mutually independent trials with the same success probability. Independent disks with one common annual failure chance fit this model if you count failed original disks. Shared power failures or different disk risks violate its assumptions.

## Count arrangements as well as one sequence

For exactly three heads in five coin flips, one arrangement is heads-heads-heads-tails-tails. Other arrangements have the same count. The binomial probability includes every such arrangement, not just the displayed sequence. For fair independent flips, sequences are equally likely; the possible head counts are not.

```formula reference
X ~ Bin(n, p)
P(X = k) = C(n, k) × p^k × (1 − p)^{n − k}
C(n, k) = n! / (k! × (n − k)!)
E[X] = n × p
Var(X) = n × p × (1 − p)
where
P: probability of measurable events, dimensionless and between zero and one
X: the number of successes, a whole number from 0 to n
~: "is distributed as", "has the distribution"
Bin(n, p): the binomial distribution with n trials and success probability p
n: the nonnegative integer number of trials
p: the common trial success probability, between 0 and 1; use the displayed mass formula away from the endpoints
k: a particular number of successes we ask about, 0 to n
P(X = k): the probability of exactly k successes
C(n, k): "n choose k", the number of ways to pick which k of the n trials succeed
!: factorial; n! = n × (n − 1) × … × 2 × 1, and 0! = 1
p^k: k copies of p multiplied together, the chance that k chosen trials all succeed
(1 − p)^{n − k}: the chance that the other n − k trials all fail
E[X]: the expected (mean) number of successes
Var(X): the variance of the number of successes
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: multiply the number of arrangements with the requested success count by the probability of one arrangement. The expected count is the trial count times the common success probability.
```

The endpoint cases are simple: success probability zero produces no successes; probability one produces success on every trial. Treat them directly rather than evaluating ambiguous powers in the general mass formula.

## Accumulating small risks

For a transfer to lose no packets, every packet must survive. Under independent loss with a fixed nonzero rate, a longer transfer has more opportunities for loss, even though each packet's risk stays unchanged. An expected loss count of one does not guarantee exactly one loss.

A fixed count of trials differs from continuing until the first success, which calls for a geometric waiting-time model. Bursty losses need a dependence model rather than an automatic binomial assumption.

## Key takeaways
- Binomial counts need fixed trials, independence and one common success probability.
- Include every arrangement giving the requested count.
- A small per-trial risk can accumulate across many trials.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
