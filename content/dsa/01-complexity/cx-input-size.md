---
id: cx-input-size
sourceLesson: cx-growth-rates
title: Input size and dominant terms
level: basic
minutes: 4
summary: Choose the right input measure and simplify a cost without forgetting its limits.
---

## What "input size" means

n should measure whatever drives the work. Usually it is obvious, but not always:

- For a list or string, n is its length.
- For a graph, cost may depend on both vertices V and edges E; state both, as in O(V + E).
- For big-number arithmetic, count **digits** or bits rather than the value. Testing every divisor up to a number’s value is linear in that value but exponential in its bit length.
- For matrices, distinguish side length from entry count. A 1,000-by-1,000 matrix has a million entries.

The number-size point is easy to get wrong, so here it is as a formula:

```formula
b = ⌊log_2(N)⌋ + 1
N ≈ 2^b
2^64 ≈ 1.8 × 10^19
M = n^2
where
N: the value of the number being tested, for example 1,000,003
b: the input size: how many bits (binary digits) it takes to write N down
log_2(N): the base-2 logarithm of N, the power you raise 2 to in order to get N
⌊x⌋: floor: round x down to the nearest whole number
≈: approximately equal to; a 64-bit number can be as large as 2^64 − 1, about 1.8 × 10^19
M: the entry count of a square matrix
n: the matrix side length, in entries
In words: adding one bit doubles the largest value you can write, so a loop that runs once per unit of value runs about 2^b times: exponential in the number of bits.
```

When you describe an algorithm's cost, always say what n is.

## Why we ignore the small stuff

Precise pair counting quickly becomes tedious and depends on what counts as one operation. The card expands that count to show which term eventually dominates.

```formula
C(n) = n(n − 1) / 2
C(n) = 0.5n^2 − 0.5n
C(1000) = 500000 − 500
C(2n) ≈ 0.5 × 4n^2 ≈ 4C(n)
A(n) = 100n
B(n) = n^2
A(50) = 5000 > B(50) = 2500
where
C(n): the number of comparisons the pairwise duplicate check makes on n items
n: the number of items in the list
≈: approximately equal to (the small 0.5 × n term is ignored)
A(n): the linear alternative’s operation count
B(n): the quadratic alternative’s operation count
>: greater than
In words: the n-squared term is a thousand times bigger than the other term at n = 1,000, and doubling n multiplies it by four whatever the constant in front.
```

1. **Keep only the fastest-growing term.** The quadratic part dominates the linear correction: at 1,000 items their contributions are 500,000 and 500.
2. **Drop constant factors.** Half the square and three times the square have the same doubling behaviour. Their constants depend on the machine and counting model; their growth shape does not.

The result is a coarse but robust label: "this algorithm is quadratic". The following asymptotic-notation lessons make this precise with Big-O, Big-Omega and Big-Theta.

> [!warning] Constants are not irrelevant in practice
> Dropping constants compares growth; it does not mean constants never matter. The card’s linear alternative loses to the quadratic one below 100 items, including its 50-item example. The later practice lessons explain when constants and hardware decide the winner.

## Key takeaways
- For integers, input size usually counts bits or digits rather than the represented value.
- State separate dimensions when several quantities drive the work.
- Dominant terms predict growth; constants can still decide the winner for small inputs.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
