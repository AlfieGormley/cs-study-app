---
id: prob-axioms-unions
title: Combine events without double-counting
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Subtract the overlap when combining events.
---

Combining failure rates starts with a practical question: can the same request appear in both groups? If so, simply adding the rates counts some requests twice.

## Combine events carefully

Probability is never negative, the whole sample space has probability one, and probabilities add for events that cannot happen together. Such events are **disjoint**. The addition axiom also covers countably many pairwise disjoint events; infinite models restrict probabilities to a specified collection of measurable events.

For overlapping events, the **addition rule** adds their probabilities and subtracts the probability of their overlap once. “Either” includes cases where both happen. For example, a request that is both slow and erroneous belongs in the union once, not twice.

The **complement** is everything outside an event. Its probability is what remains from one. This often makes “at least one failure” easier: work out the chance of no failures first.

## A bound when overlap is unknown

The **union bound** adds the individual probabilities without subtracting overlap. It cannot underestimate the probability that at least one event happens, and it requires no independence assumption. It may overestimate badly when failures occur together.

```formula reference
P(B_1 ∪ B_2 ∪ … ∪ B_n) ≤ n × p
where
B_1, B_2, …, B_n: n "bad" events, for example "request i hits a slow server"
n: how many bad events there are
p: an upper limit on each bad event's probability, so P(B_i) ≤ p for every i
P: probability; probabilities are dimensionless and apply to measurable events
∪: union, "at least one of these happens"
…: and so on, for every event in between
≤: less than or equal to
In words: the chance that any bad event occurs is at most the event count times a shared upper bound on each event's probability, whether or not the events are independent.
```

If the sum exceeds one, use one as the trivial upper bound: probabilities cannot exceed certainty. The bound is useful for budgeting many small risks, not for claiming their exact combined probability.

> [!analogy] Real-world analogy: overlapping guest lists
> Two organisers count their invitees, but some people appear on both lists.
>
> **How it maps:** Adding list sizes counts shared guests twice; subtracting the overlap counts each invited person once.
>
> **Where it stops:** Unequally likely outcomes need probability weights, not just headcounts.

## Key takeaways
- Subtract overlap to obtain an exact union probability.
- Adding probabilities gives an upper bound without independence.
- A bound above one provides no useful extra information.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
