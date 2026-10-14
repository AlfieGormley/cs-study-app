---
id: cx-variable-step-loops
sourceLesson: cx-analysing-code
title: Loops with a variable step
level: intermediate
minutes: 3
summary: Sum the shrinking inner counts in a harmonic loop.
---

Here n is the positive input size. This example varies the step of the inner range instead of varying its endpoint.

## A harmonic loop

The second trap is the **harmonic** loop:

```python
for i in range(1, n + 1):
    # i is the step; the stop n is excluded.
    for j in range(0, n, i):
        work()
```

The inner range starts at zero, stops before the bound and jumps by the outer variable’s value. Its count is the input bound divided by that step, rounded up. Sum those actual counts:

```formula
W(n) ≈ n/1 + n/2 + n/3 + … + n/n
W(n) ≈ n H(n)
H(n) = 1 + 1/2 + … + 1/n ≈ ln(n)
W(1000) ≈ 1000 × 7.5 = 7500
W(n) = Σ_{i=1}^{n} ⌈n/i⌉
W(1000) = 8053
where
W(n): the total number of work() calls
n: the input size
H(n): the n-th harmonic number, the sum of the fractions 1/1 to 1/n
ln(n): the natural logarithm of n (base e ≈ 2.718); about 0.69 × log_2(n)
…: "and so on"
≈: approximately equal to (each pass runs n / i times rounded up; H(1000) ≈ 7.49)
Σ_{i=1}^{n}: sum over all step sizes from one through the bound
i: the positive step size set by the outer loop
⌈ ⌉: ceiling: round up to a whole number of iterations
In words: the inner loop shrinks as 1/i, and those fractions add up to only about the logarithm of n, so the total is about n log n, not n squared.
```

So this is **Θ(n log n)**, where n is the input bound, rather than quadratic. Similar sums appear in sieves; the Sieve of Eratosthenes has the tighter Θ(n log log n) bound, where the second logarithm is applied to the first. They also occur in graph and number-theory problems.

| Pattern | Approximate count |
|---|---|
| Inner bound grows with outer | half the square |
| Doubling variable | logarithmic |
| Squared variable within bound | square root |
| Doubling outer, inner to outer | less than twice the bound |
| Inner step equals outer | bound times natural log |

## Key takeaways
- A range step can change the inner length even when the stop stays fixed.
- The harmonic loop adds many shrinking contributions rather than equally sized passes.
- Summing actual counts can reveal a tighter bound than multiplying maximum bounds.

## Further reading
- [Harmonic series — Wikipedia](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics))
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
