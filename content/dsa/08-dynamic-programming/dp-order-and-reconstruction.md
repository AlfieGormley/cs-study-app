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

Every DP state depends on some others. For a recurrence evaluated once per state, those dependencies must form a **directed acyclic graph** (DAG): no state may depend, directly or indirectly, on itself. Bottom-up evaluation is just a topological order of that DAG. A strictly shrinking measure (a smaller index, a shorter interval, a smaller remaining budget) is the usual proof that no cycle exists.

If the dependencies do form a cycle, plain memoisation recurses forever. Cyclic equations (such as Bellman equations in decision-making under uncertainty) need different, iterative fixed-point methods such as value iteration.

- If `dp[i]` depends on larger `i`, loop `i` downwards.
- If `dp[i][j]` depends on `[i-1][j]` and `[i][j-1]`, loop rows then columns, both upwards.
- If an interval depends on shorter intervals, loop by length.

Memoisation finds the order automatically, which is why it's a good first draft.

## Step 5: answer and reconstruction

Say which state is the answer (`dp[0]`, `dp[n]`, `max(dp)`, ...). Then, if the problem wants the actual solution, either:

- **Store the choice** that achieved each state's best value, in a parallel array, and follow it from the answer state; or
- **Recompute**: walk from the answer state and, at each step, check which option reproduces the stored value.

Following stored choices takes time proportional to the number of reconstruction steps plus output construction. Rechecking alternatives can cost more: include the number of candidates examined at each step.

> [!analogy] Real-world analogy: a route log on a long drive
> At the end of a drive, the trip computer can tell you the total distance, but not which turns you took. If you jotted down the turn at every junction, you can read the whole route back. If you didn't, you can still work it out by checking, at each junction, which road is consistent with the distances you remember.
>
> **How it maps:** the total distance is the DP value at the answer state. The jotted turns are the stored choices, followed back from the answer. Checking which road fits the remembered distances is the recompute method: at each state, find the option that reproduces the stored value.
>
> **Where it stops:** a driver only logs the junctions they actually passed. A DP stores a choice for every state, including the many that are not on the final route, because it doesn't know the route until the end.

## Choosing between prefix and suffix states

Both work for most sequence problems. Pick whichever makes the recurrence read naturally:

- **Suffix** (`f(i)` records answer for `s[i:]`): the first decision is "what do I do at i?". It matches top-down recursion well.
- **Prefix** (`dp[i]` records answer for `s[:i]`): the last decision is "what was the final piece?". It matches left-to-right loops.

## Keeping a path while saving rows

A rolling table keeps only the latest row or two, so the older rows a traceback would need are gone. Keep per-cell choices when memory permits, or do extra work to recover them. Hirschberg’s technique (1975, for longest common subsequence and alignment) computes costs forwards from the start and backwards from the end to a middle row, picks the column where the two meet on an optimal path, and recurses on the two halves. For strings of lengths m and n, it keeps O(mn) time while using only linear extra storage plus the output. One reverse rolling pass alone does not recover every choice.

## Key takeaways
- Finite once-per-state evaluation requires acyclic dependencies.
- Store winning choices or recompute them to recover a solution.
- Prefix and suffix states are both valid when their recurrences match.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
- [Hirschberg’s algorithm](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
