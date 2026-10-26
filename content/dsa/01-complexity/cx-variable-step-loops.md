---
id: cx-variable-step-loops
sourceLesson: cx-analysing-code
title: Loops with a variable step
level: intermediate
minutes: 2
summary: Sum the shrinking inner counts in a harmonic loop.
---

An inner loop can become shorter even when its endpoint stays fixed. Here n is a positive input bound and `work()` is one constant-cost step.

## Watch the step size

```python
for i in range(1, n + 1):
    # Start at zero; exclude n.
    for j in range(0, n, i):
        work()
```

With step one, the inner loop visits every position. With step two it visits about half; step three about a third. Each length is the bound divided by the step, rounded up. The total does not equal the largest inner length multiplied by the outer count.

These contributions form a **harmonic sum**, whose growth is logarithmic. Multiplying by the original bound gives Θ(n log n) work. Rounding adds less than one extra step per outer pass, so it cannot change that class.

## Why a logarithmic factor appears

Group step sizes into bands that double: one, then two to three, then four to seven, and so on. A later band has about twice as many step sizes, but each inner loop is about half as long. Each complete band therefore contributes work proportional to the original bound. There are logarithmically many bands.

This differs from a geometric sum of inner lengths. In a geometric sum, doubling the index halves the entire next contribution. Here there are many step sizes between successive powers of two, and their combined contributions matter.

| Inner-loop pattern | Total growth |
|---|---|
| Same full range each time | quadratic |
| Length grows with outer position | quadratic |
| Doubling outer value sets inner length | linear |
| Outer value sets the inner step | linear times log |

The shared lesson is to read the actual range. Similar-looking nested loops need not have similar cost.

## Key takeaways
- A larger step means fewer inner iterations.
- Harmonic contributions accumulate across logarithmically many bands.
- Integer rounding does not change this loop's tight growth bound.

## Further reading
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
