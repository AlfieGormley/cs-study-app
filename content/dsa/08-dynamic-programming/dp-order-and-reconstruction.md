---
id: dp-order-and-reconstruction
title: Evaluate dependencies and recover choices
level: basic
minutes: 3
summary: Finite once-per-state evaluation requires acyclic dependencies.
sourceLesson: dp-method
---

Once the state and transitions are correct, decide when each answer becomes available and how to recover the choices behind it.

## Step 4: evaluation order

Every state depends on some others. For a finite recurrence evaluated once per state, those dependencies must form a **directed acyclic graph**. Cyclic Bellman equations can require fixed-point methods such as value iteration; plain memoisation does not solve a dependency cycle. Bottom-up evaluation is just a topological order of that DAG.

- If `dp[i]` depends on larger `i`, loop `i` downwards.
- If `dp[i][j]` depends on `[i-1][j]` and `[i][j-1]`, loop rows then columns, both upwards.
- If an interval depends on shorter intervals, loop by length.

Memoisation finds the order automatically, which is why it's a good first draft.

## Step 5: answer and reconstruction

Say which state is the answer (`dp[0]`, `dp[n]`, `max(dp)`, ...). Then, if the problem wants the actual solution, either:

- **Store the choice** that achieved each state's best value, in a parallel array, and follow it from the answer state; or
- **Recompute**: walk from the answer state and, at each step, check which option reproduces the stored value.

Following stored choices takes time proportional to the number of reconstruction steps plus output construction. Rechecking alternatives can cost more: include the number of candidates examined at each step.

## Choosing between prefix and suffix states

Both work for most sequence problems. Pick whichever makes the recurrence read naturally:

- **Suffix** (`f(i)` records answer for `s[i:]`): the first decision is "what do I do at i?". It matches top-down recursion well.
- **Prefix** (`dp[i]` records answer for `s[:i]`): the last decision is "what was the final piece?". It matches left-to-right loops.

## Keeping a path while saving rows

A rolling table discards older rows, so its final row alone cannot support a direct traceback. Keep per-cell choices when memory permits, or do additional work to recover them. Hirschberg’s alignment technique computes forward and backward costs to a middle row, chooses a compatible split column, and recurses on both halves. For strings of lengths m and n, this preserves O(mn) time for nonempty strings with linear auxiliary storage plus the output; one reverse rolling pass alone does not recover every choice.

## Key takeaways
- Finite once-per-state evaluation requires acyclic dependencies.
- Store winning choices or recompute them to recover a solution.
- Prefix and suffix states are both valid when their recurrences match.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
- [Hirschberg’s algorithm](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
