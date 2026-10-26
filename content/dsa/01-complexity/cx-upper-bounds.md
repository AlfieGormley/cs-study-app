---
id: cx-upper-bounds
sourceLesson: cx-asymptotic-notation
title: Proving an upper bound
level: basic
minutes: 2
summary: Use fixed constants to prove or disprove a Big-O claim.
---

Big-O gives an eventual upper bound on growth. It does not promise an exact operation count, and it does not itself mean "worst case". First choose the cost function being discussed, such as worst-case comparisons over inputs of each size.

## One fixed multiplier must keep working

For a nonnegative cost, the definition is:

```formula essential
f(n) = O(g(n))
0 ≤ f(n) ≤ c g(n) for all n ≥ n_0
where
f(n): the nonnegative cost being bounded, in counted operations
g(n): the eventually positive comparison function, in the same cost model
n: the input size, a nonnegative integer
O: Big-O; the first line holds when fixed constants make the second line true
c: one positive multiplier independent of input size
n_0: a fixed starting input size beyond which the bound must always hold
≤, ≥: at most, at least
In words: beyond a fixed starting size, the cost never exceeds one fixed multiple of the comparison function.
```

The multiplier absorbs constant factors. The threshold allows a finite set of small inputs to behave differently. Neither may keep changing as the input grows.

For example, a scan with fixed setup work still has a linear upper bound. Choose a multiplier larger than its per-item cost; beyond some point, the spare allowance covers the setup on every later input. Matching only the per-item cost leaves no allowance for positive setup work.

A quadratic cost cannot have a linear upper bound. As inputs grow, work per item keeps increasing, so every proposed fixed linear multiplier is eventually exceeded.

## True can still be unhelpful

Binary search halves a sorted range and has a logarithmic worst-case comparison count, assuming constant-cost indexing and comparisons. It also has a linear upper bound, because linear growth eventually exceeds logarithmic growth. Both statements are true; the logarithmic bound is more informative.

Testing a few sizes cannot prove a bound for every later size. Use the mechanism or a mathematical argument. A ratio that grows without bound is one way to disprove an upper bound; oscillating ratios may require returning to the definition.

## Key takeaways
- Big-O permits one fixed multiplier and one fixed starting threshold.
- A valid bound must hold at every sufficiently large input size.
- Prefer a tight useful upper bound over a needlessly loose one.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
