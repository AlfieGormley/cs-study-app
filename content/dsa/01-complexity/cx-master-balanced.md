---
id: cx-master-balanced
sourceLesson: cx-recurrences
title: Master Theorem: balanced work
level: advanced
minutes: 2
summary: Handle matching costs and logarithmic factors with the second case.
---

When outside work matches the recursion tree's leaf growth, work is spread across many levels. The missing logarithm in a guessed answer often comes from forgetting to add those levels.

## Matching work adds a level factor

Four half-size children with quadratic outside work illustrate the idea. Each child does a quarter of the parent's outside work, but there are four children. Their combined cost matches the parent's. Every level therefore has quadratic total work, and there are logarithmically many levels. The result is Θ(n² log n), where n is the original input size.

The balanced case also has a useful logarithmic-factor extension:

```formula essential
f(n) = Θ(n^c(log(n))^k)
T(n) = Θ(n^c(log(n))^{k+1})
where
f(n): outside work in an equal-size Master Theorem recurrence
T(n): total work with bounded positive base cases
n: input size
c: the critical exponent determined by the fixed branching and shrink factors
k: a fixed nonnegative logarithm exponent
log: logarithm to a fixed base greater than one
Θ: a tight growth bound
In words: matching the critical power, possibly with a nonnegative power of a logarithm, adds one more logarithm power when work is summed across levels.
```

The exact equal-level picture applies when there is no extra logarithm factor. For two half-size children with linear-times-log outside work, the total size across a level stays the same, but the logarithm decreases gradually as subproblems shrink. Adding those declining level costs gives Θ(n(log n)²).

This is not the root-dominated case: one extra logarithm is not a fixed positive power gap. Nor does the displayed extension cover a negative logarithm exponent. Check the version of the theorem being used before applying a shortcut.

## Key takeaways
- Equal work per level must be multiplied by the number of levels.
- The nonnegative-log-power extension adds one logarithm power.
- A logarithmic factor alone is not a polynomial gap.

## Further reading
- [MIT: Master theorem, including power gaps and regularity](https://people.csail.mit.edu/thies/6.046-web/master.pdf)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
