---
id: cx-input-size
sourceLesson: cx-growth-rates
title: Input size and dominant terms
level: basic
minutes: 2
summary: Choose the right input measure and simplify a cost without forgetting its limits.
---

Calling an algorithm "linear" is incomplete until you say what it is linear in.

## Choose the measure that drives the work

- For a list, n usually counts items.
- For a graph, V counts vertices and E counts edges. A traversal may need O(V + E) work; neither dimension can be dropped without a relationship between them.
- For an image, count pixels when the algorithm visits pixels. Doubling both dimensions quadruples pixel count.
- For a number, input length counts its digits or bits, rather than its numeric value.

Adding one bit approximately doubles the range of positive integers representable at that length. A primality test that tries every possible divisor up to the number's value can therefore take exponentially many iterations in the bit length. An early exit on composite inputs does not fix the prime-input worst case. Division on large integers also costs more than a single fixed-size operation.

Testing only up to the square root reduces work substantially, but remains exponential in bit length. A polynomial bound in numeric value need not be polynomial in the encoded input length; this distinction is called **pseudo-polynomial time**.

## What dominant terms tell you

An all-pairs comparison has a quadratic main term and a smaller linear correction. For large inputs, the quadratic part determines scaling. Dropping fixed multipliers and lower-order terms produces a useful growth label.

It does not produce an exact runtime or a universal winner. A simple quadratic implementation can beat a linear-times-log implementation over a small input range because of lower setup and per-step costs. The slower growth rate wins eventually under comparable fixed cost models, but the crossover must be established rather than assumed.

## Key takeaways
- Always name the input measure, including independent dimensions.
- Numeric value and encoded length can give very different complexity descriptions.
- Dominant growth predicts scaling, while constants still matter at finite sizes.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
