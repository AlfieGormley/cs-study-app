---
id: prob-binomial-reliability
title: Apply binomial counts to fleets and quorums
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: Disk counts refer to the original fleet, not replacements.
---

## Fleets and quorums

In a hypothetical fleet of 1,000 disks, suppose each independently has a 2% probability of failing during a year. The number of original disks that fail is binomial:

```formula
D ~ Bin(1000, 0.02)
E[D] = 1000 × 0.02 = 20
σ = √(1000 × 0.02 × 0.98) ≈ 4.4
where
D: the number of the original 1,000 disks that fail in the year
~: "is distributed as"
Bin(1000, 0.02): binomial with 1,000 trials (disks) and failure probability 0.02 (2%)
E[D]: the expected number of failures
σ: sigma, the standard deviation of D, the square root of trials × probability × (1 − probability), here 1000 × 0.02 × 0.98
√: the square root
0.98: the chance a disk survives the year, 1 − 0.02
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: expect about 20 failures, typically give or take 4 or 5.
```

This does not count failures of replacement disks. A spare-stock policy also needs a tolerated shortage probability and the time needed to replenish spares; the mean alone is insufficient.

A fixed 5-node majority-quorum cluster cannot form a majority when 3 or more nodes are down. If each node is independently down with probability 1% at a sampled instant:

```formula
P(N ≥ 3) = C(5, 3) × p^3 × q^2
  + C(5, 4) × p^4 × q + p^5
P(N ≥ 3) ≈ 10 × 10^{−6} ≈ 1 × 10^{−5}
where
N: the number of the 5 nodes that are down
P: probability; probabilities are dimensionless and apply to measurable events
p: the probability one node is down, 0.01
q: the probability one node is up, 1 − p = 0.99
C(5, 3): "5 choose 3", the ways to pick which 3 nodes are down, which is 10
C(5, 4): the ways to pick which 4 are down, which is 5
p^3: 3 copies of p multiplied together; p^4 and p^5 likewise
≥: greater than or equal to
≈: approximately equal to
10^{−6}: one millionth
In words: losing quorum needs 3, 4 or 5 nodes down at once; the "exactly 3" term dominates at about 10 × 0.01³, roughly one chance in 100,000.
```

That is about 1 in 100,000, equivalent to roughly 5.2 expected minutes per 365-day year if these marginal probabilities remain constant. This estimates quorum loss due to node downtime, not total service unavailability: network partitions, leader elections and recovery also matter. Correlated failures invalidate the product model.

## Key takeaways
- Disk counts refer to the original fleet, not replacements.
- Quorum-loss estimates require independent node downtime and omit other failure causes.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
