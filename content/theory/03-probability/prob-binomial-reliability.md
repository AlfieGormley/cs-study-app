---
id: prob-binomial-reliability
title: Apply binomial counts to fleets and quorums
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: Disk counts refer to the original fleet, not replacements.
---

A model of failed components answers a narrower question than “will the service work?” Specify the population, time window and failure condition before using a binomial count.

## Count an original fleet

Suppose every original disk has the same annual failure probability and the failures are independent. The number of those disks that fail during the year is binomial. It does not count failures of replacements installed during the year: those add new exposures outside the original set of trials.

The expected failure count is useful for average demand, but stocking exactly that many spares does not control shortage risk. A policy also needs a tolerated shortage probability and replenishment time. Shared manufacturing defects or infrastructure can make a simple independent model optimistic.

## Translate quorum rules into count events

A fixed five-node **majority quorum** needs three reachable cooperating members. Considering node downtime alone, up to two nodes can be down while a majority remains; three or more down prevents one.

Under identical independent downtime chances at a sampled instant, use the binomial tail covering three, four and five failed nodes. Counting one specific group of three misses the other groups that can fail. Counting at least one failure asks about a different event that the cluster can tolerate.

Even an accurate node-downtime estimate is not total service unavailability. Network partitions, elections, recovery and routing may stop service while enough nodes are technically up. Turning a sampled-instant probability into expected annual downtime also assumes appropriate stable marginal probabilities.

## Key takeaways
- State whether the population includes replacement components.
- Mean demand alone does not set a spare-stock policy.
- Quorum loss depends on a threshold count and still omits other service failure causes.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
