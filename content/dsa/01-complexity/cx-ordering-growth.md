---
id: cx-ordering-growth
sourceLesson: cx-asymptotic-notation
title: Ordering growth with limits
level: basic
minutes: 2
summary: Use ratios and the growth ladder to compare unfamiliar cost functions.
---

Compare growth by asking whether the gap between two costs keeps widening. Here n is input size; logarithms have a fixed base greater than one.

## Ratios give a useful test

Divide the first eventually positive function by the second and consider increasingly large inputs:

| Ratio approaches | What it establishes |
|---|---|
| Zero | the first grows strictly more slowly |
| A fixed positive number | the same tight growth rate |
| Infinity | the first grows strictly faster |

A ratio approaching zero is called **little-o**. These are sufficient conclusions when the limit exists. A tight bound does not require convergence: a ratio can keep oscillating between two positive constants. If there is no limit, inspect bounds directly.

## A growth ladder

| Slower to faster | Example mechanism |
|---|---|
| Constant | index a fixed-size array slot |
| Logarithmic | repeatedly halve a search range |
| Square root | count up to the square root of a numeric bound |
| Linear | scan every item |
| Linear times log | merge over logarithmically many levels |
| Quadratic, then cubic | all pairs, then all triples |
| Fixed-base exponential | enumerate subsets |
| Factorial | enumerate all orderings |

This compares eventual growth with the same input measure. A square-root divisor search measured in numeric value is still exponential when measured in bit length.

Factorial counts multiply the positive integers up to the item count. Taking a logarithm turns that product into a sum of logarithms. There are at most n terms each no larger than the logarithm of n, and a constant fraction are within a constant of that largest logarithm. Thus the logarithm of the factorial has Θ(n log n) growth. This underlies the worst-case comparison-sorting lower bound.

A **quasi-polynomial** example raises input size to its logarithm. It eventually outgrows every fixed polynomial yet remains below a fixed-base exponential. Comparing both expressions as powers of the same base reveals the order; a single measured size cannot prove it.

## Key takeaways
- Ratio limits reveal relative growth when the limit exists.
- A finite-range measurement is not a proof of eventual order.
- Factorial growth is enormous, but its logarithm is linear times log.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
