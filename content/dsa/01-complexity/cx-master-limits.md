---
id: cx-master-limits
sourceLesson: cx-recurrences
title: When the Master Theorem does not fit
level: advanced
minutes: 2
summary: Recognise unsupported recurrences and prove a guessed bound by induction.
---

The Master Theorem is a shortcut with assumptions. When a recurrence falls outside them, inspect its actual work instead of forcing it into a case.

## Recognise the mismatch

- Subtracting one item is not shrinking by a fixed fraction. A single recursive chain with a full scan at each step has linearly many levels of decreasing linear work, giving quadratic total work.
- Two calls each one item smaller create exponential branching across a linear depth.
- Unequal-size children do not fit the equal-size theorem. Recursion trees or Akra–Bazzi may still work.
- A number of children or shrink factor that varies with input size needs a different analysis.
- Outside work smaller than the critical growth by only a logarithm falls between the leaf case and the nonnegative-log-power balanced version taught here.

For that last example, two half-size calls plus linear work divided by a logarithm give Θ(n log log n), where n is input size. The next lessons explain the slowly accumulating factor. Some stronger theorem statements cover this case directly; the limitation is in the stated version.

## Guess, then prove with the same constants

A recursion tree can suggest a bound. **Mathematical induction** then checks a base case and shows that assuming the bound for smaller inputs establishes it for the current input with the same fixed multiplier.

Here is a failed attempt for two half-size calls plus linear work:

```formula essential
T(n) = 2T(n/2) + n
T(n) ≤ 2c(n/2) + n = (c + 1)n
where
T(n): counted work on input size n, with a fixed positive base case
n: positive input size; use powers of two for this argument
c: the fixed multiplier in the proposed linear induction bound
≤: at most
In words: assuming a linear bound for the children produces a larger multiplier for the parent, so the proposed induction does not close.
```

Calling the final expression "linear" does not repair the proof. Repeating that multiplier increase through the levels hides the missing logarithmic factor. A linear-times-log guess has enough room for each level's added work. Its proof must cover a suitable base case; the logarithm at one is zero, so handle that size separately.

## Key takeaways
- Check the recurrence form and the growth-case conditions.
- Induction must preserve one fixed bound through every level.
- A failed proof suggests a better guess but does not prove that guess.

## Further reading
- [MIT: Master theorem, including power gaps and regularity](https://people.csail.mit.edu/thies/6.046-web/master.pdf)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
