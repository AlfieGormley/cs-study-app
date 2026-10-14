---
id: cx-master-balanced
sourceLesson: cx-recurrences
title: Master Theorem: balanced work
level: advanced
minutes: 2
summary: Handle matching costs and logarithmic factors with the second case.
---

The previous unit defined the critical exponent from the number of subproblems and their shrink factor. Here n is the input size. This unit covers the case where outside work matches that critical growth, possibly with logarithmic factors.

## Case 2

**Case 2: f is about the same as n^c.** Every level does roughly equal work, so you multiply by the number of levels, which adds a log factor:

```formula
f(n) = Θ(n^c × (log n)^k)  for some k ≥ 0
T(n) = Θ(n^c × (log n)^{k+1})
where
f(n): the work outside the recursive calls
n: the input size
c: the critical exponent, log_b(a)
log: the logarithm (any fixed base; it only changes a constant)
k: a fixed number of at least 0; k = 0 is the common case, f(n) = Θ(n^c)
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
≥: greater than or equal to
In words: if the root's work matches the leaf count (up to log factors), every level costs about the same and the answer gains one more log factor.
```

(Levels are exactly equal only when k = 0; for larger k, summing the slowly changing level costs still adds one log power.)

## Key takeaways
- Matching root and leaf costs adds a logarithmic factor across the levels.
- The stated logarithmic-factor extension adds one further log power.
- Apply the case’s conditions before reading off the result.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
