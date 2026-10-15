---
id: prob-reliability-models
title: Model series and redundant availability
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Series systems require every component to work.
---

## Reliability: the engineer's favourite use

Independence makes system reliability easy to estimate. **System availability** is the fraction of time a component is up and serving.

In a **series system** (components that must all work), multiply the availabilities. A request that passes through three services, each independently up 99.9% of the time, in a model with no other causes of failure:

```formula
A_s = a_1 × a_2 × a_3
A_s = 0.999 × 0.999 × 0.999 ≈ 0.997
where
A_s: the availability of the whole chain, the fraction of time every service is up at once
a_1, a_2, a_3: the availability of each service, here 0.999 (99.9%)
≈: approximately equal to (0.997003, rounded)
In words: the chain works only when all three work, so with independent failures the chance is the product, about 99.7%.
```

So the chain is down about 0.3% of the time, roughly three times worse than any single service. Long chains of dependencies erode availability.

With **parallel redundancy** (replicas where any one working copy is sufficient, with ideal routing and failover), multiply the failure probabilities. Three replicas, each down 1% of the time independently:

```formula
P(D) = q^3 = 0.01^3 = 0.000001
1 − P(D) = 0.999999
where
P: probability of measurable events, dimensionless and between zero and one
q: the probability that one replica is down, here 0.01 (1%)
q^3: three copies of q multiplied together, one factor per independent replica
D: the event "all three replicas are down at once"
P(D): the probability of D
In words: the cluster fails only when all three replicas are down together, about one moment in a million, giving "six nines" (99.9999%) availability.
```

> [!warning] Real failures are correlated
> The six-nines figure assumes the replicas fail independently. Put them in the same rack, region, power feed or software version and a single event takes them all down. Separating replicas across failure domains can reduce shared infrastructure risks, while a bad deployment across all replicas can still defeat redundancy. When an estimate looks too good, the independence assumption is usually the culprit.

## Key takeaways
- Series systems require every component to work.
- Parallel replicas help only under the stated independence and failover assumptions.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
