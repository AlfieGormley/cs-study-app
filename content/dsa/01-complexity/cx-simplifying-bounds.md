---
id: cx-simplifying-bounds
sourceLesson: cx-asymptotic-notation
title: Simplifying asymptotic expressions
level: basic
minutes: 2
summary: Drop dominated terms while preserving distinctions between exponential bases.
---

Simplifying a cost means keeping the part that determines eventual growth. Here n is input size; log denotes a logarithm with a fixed base greater than one.

## Remove details only when the bound permits it

- Fixed positive multipliers do not change a tight growth class.
- In a finite sum of nonnegative familiar growth functions, keep the fastest-growing term. For example, cubic work eventually dominates quadratic-times-log work and fixed overhead.
- Two sequential phases add their costs. Independent nested phases multiply their counts.
- Independent input dimensions must remain separate unless their relationship is known.

The rule is about growth, not exact equality. Two functions can share a quadratic upper bound while having quite different values, or even different tight growth rates. A linear function and a quadratic function both have a quadratic upper bound.

## Logarithm bases and exponential bases behave differently

Changing between two fixed logarithm bases multiplies the value by a constant. It changes an exact count, but not the logarithmic growth class. The useful conversion is available as reference:

```formula reference
log_a(n) = log_b(n) / log_b(a)
where
log_a, log_b: logarithms to bases a and b
a, b: fixed bases greater than one
n: positive input size
In words: changing between two fixed logarithm bases rescales the value by a fixed multiplier, so the growth class stays the same.
```

Changing an exponential base is different. Choosing among three possibilities per item creates more candidates than choosing among two. Their ratio itself grows exponentially, so a constant multiplier cannot absorb that difference.

A fixed power of a logarithm eventually grows more slowly than any positive power of input size. A fixed polynomial eventually grows more slowly than an exponential with fixed base greater than one. "Eventually" matters: a very large polynomial exponent or coefficient can delay that order far beyond practical inputs.

## Key takeaways
- Drop coefficients and dominated terms when describing eventual growth.
- A shared upper bound is not a statement of equal cost.
- Fixed log bases change constants; exponential bases can change growth classes.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
