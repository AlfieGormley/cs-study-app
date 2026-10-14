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

The inner loop steps through 0 to n in jumps of i, so it runs about n / i times. Add up all the passes:

```formula
W(n) ≈ n/1 + n/2 + n/3 + … + n/n
W(n) ≈ n × H(n)
H(n) = 1 + 1/2 + … + 1/n ≈ ln(n)
W(1000) ≈ 1000 × 7.5 = 7500
where
W(n): the total number of work() calls
n: the input size
H(n): the n-th harmonic number, the sum of the fractions 1/1 to 1/n
ln(n): the natural logarithm of n (base e ≈ 2.718); about 0.69 × log_2(n)
…: "and so on"
≈: approximately equal to (each pass runs n / i times rounded up; H(1000) ≈ 7.49)
In words: the inner loop shrinks as 1/i, and those fractions add up to only about the logarithm of n, so the total is about n log n, not n squared.
```

So this is **Θ(n log n)**, not n^2. It appears in sieves (such as the Sieve of Eratosthenes, which is even tighter at n log log n, where log log n is the logarithm of the logarithm) and in some graph and number theory problems.

| Pattern | Count |
|---|---|
| inner to i | n^2 / 2 |
| i *= 2 | log n |
| i*i <= n | √n |
| doubling outer, inner to i | < 2n |
| inner step i | n ln n |

## Key takeaways
- A range step can change the inner length even when the stop stays fixed.
- The harmonic loop adds many shrinking contributions rather than equally sized passes.
- Summing actual counts can reveal a tighter bound than multiplying maximum bounds.

## Further reading
- [Harmonic series — Wikipedia](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics))
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
