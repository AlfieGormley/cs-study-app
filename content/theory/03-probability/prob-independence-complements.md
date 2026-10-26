---
id: prob-independence-complements
title: Test independence and use complements
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Independence is an equality of probabilities.
---

Two events are **independent** when learning that one occurred leaves the chance of the other unchanged, whenever that conditioning event has positive probability. Physical separation does not establish this property.

## Independence is a model claim

```formula essential
P(A ∩ B) = P(A) × P(B)
P(A | B) = P(A)   if P(B) > 0
where
P: probability of measurable events, dimensionless and between zero and one
A, B: two events
P(A ∩ B): the probability that both A and B happen
P(A), P(B): the separate probabilities of A and of B
P(A | B): the probability of A given that B happened (| is read "given")
In words: two events are independent when the chance of both is the product of their chances; equivalently, learning that B happened leaves A's chance unchanged.
```

This relationship distinguishes independence from mere lack of an obvious connection. Two events can share parts of an experiment and still be independent.

For independent fair dice, knowing the total is seven leaves the first die equally likely to show any face. Knowing the total is eight rules out a first die of one, changing its distribution. Check the relevant probabilities rather than the names of the events.

**Disjoint** events with positive probabilities are dependent: learning that one happened rules out the other. “Cannot happen together” is different from “learning one changes nothing”.

## At least one means not none

For several calls, “at least one slow” is the complement of “all fast”. If the calls are mutually independent, multiply their fast probabilities and subtract the result from one. Directly adding slow probabilities generally double-counts cases with several slow calls.

Adding more independent calls with a nonzero chance of slowness increases the chance of encountering at least one slow call. It does not make a slow call certain for any fixed finite number when each can still be fast.

If calls share an overloaded backend, the complement identity still holds. It is the multiplication of unchanged probabilities that needs reconsideration. Pairwise independence alone is insufficient for multiplying an entire sequence.

## Key takeaways
- Independence concerns probabilities, not physical separation.
- Positive-probability disjoint events are dependent.
- Complement reasoning is general; multiplying across calls needs the appropriate independence.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
