---
id: cx-akra-bazzi-examples
sourceLesson: cx-recurrences
title: Akra–Bazzi worked examples
level: advanced
minutes: 2
summary: Apply the general method to linear selection and a gap between Master Theorem cases.
---

Use the distribution of work to understand an Akra–Bazzi answer before evaluating an integral. Here n is the current input size, with bounded positive base cases.

## Selection: leave a fixed fraction out

Median-of-medians selection groups items into fives, recursively finds a pivot from the group medians, then recurses only into the relevant partition. Its worst-case analysis bounds child sizes by about one fifth and seven tenths of the parent, with rounding and a constant-sized boundary correction. This is an upper-bound recurrence for the algorithm, not an exact equality for every input.

Those fractions total less than the whole input. With linear partitioning work, the recursive contribution shrinks geometrically once inputs are large enough. The resulting worst-case bound is linear. The small rounding corrections are handled by the base threshold; they do not remove the fixed gap below the full parent size.

## A logarithmic gap accumulates slowly

Consider this recurrence for sufficiently large inputs, stopping at a fixed size above one:

```formula essential
T(n) = 2T(n/2) + n/log_2(n)
T(n) = Θ(n log_2(log_2(n)))
where
T(n): total work, with bounded positive cost below the fixed base threshold
n: input size; use powers of two to visualise the levels
log_2: base-two logarithm; the outer logarithm is applied to the inner result
Θ: a tight growth bound
In words: outside work slightly below linear still accumulates across the tree, adding a slowly growing log-log factor to the linear leaf cost.
```

Each complete level contains the same total item count, but its outside work is divided by the logarithm of the current subproblem size. Looking upward from the base, those denominators grow in roughly consecutive steps. The level contributions therefore form a harmonic sum over logarithmically many levels. That adds the logarithm of a logarithm.

The result lies between linear and linear-times-log growth. It is not covered by the nonnegative-log-power balanced case or the leaf case requiring a fixed positive power gap. Akra–Bazzi's accumulated outside-work correction distinguishes it without pretending those conditions hold.

## Key takeaways
- A fixed gap below the parent size can support linear selection.
- Real algorithm recurrences may be upper bounds with rounding corrections.
- Slightly sublinear outside work can still add a growing factor across levels.

## Further reading
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
