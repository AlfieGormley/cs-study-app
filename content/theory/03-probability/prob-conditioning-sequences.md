---
id: prob-conditioning-sequences
title: Condition on evidence and draw sequences
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Condition only on events with positive probability.
---

Evidence changes which outcomes are still possible and how they are weighted. **Conditional probability** asks about an event within the cases where the evidence holds.

## Change the group you are considering

Suppose two independent fair dice total eight. The remaining ordered pairs are (2,6), (3,5), (4,4), (5,3) and (6,2). A first die of one is now impossible, and a first die of three occurs in one of the five remaining cases. Using the original six-face probability would ignore the evidence.

```formula reference
P(A | B) = P(A ∩ B) / P(B)
where
P: probability of measurable events, dimensionless and between zero and one
P(A | B): the probability of A given B; the vertical bar | is read "given" and means "once we know B happened"
A: the event we are asking about
B: the event we already know happened; P(B) must be greater than 0
P(A ∩ B): the probability that A and B both happen (∩ means "and", both together)
P(B): the probability of B
In words: Restrict attention to the positive-probability evidence and ask what fraction of those cases also satisfy the event of interest.
```

This elementary ratio requires a conditioning event with positive probability. In infinite models, a possible event can have probability zero; conditioning there requires a more general construction.

## Sequences change their own conditions

For two events to happen together, the **multiplication rule** combines the chance of the first with the chance of the second given the first. It does not assume independence.

Draw cards from a uniformly shuffled standard deck without replacement. After drawing an ace, there are fewer aces and fewer cards left. The second draw must use that changed deck. Reusing the original ace probability would model replacement instead.

The same reasoning applies to retries: if the first failure indicates an outage, the next attempt may have a different success chance. Multiplying unchanged per-attempt chances is justified only when the model supports it.

## Key takeaways
- Conditioning changes the reference group to cases consistent with evidence.
- Sequence probabilities use the updated condition at each step.
- Without replacement, an earlier draw changes the next draw's chances.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
