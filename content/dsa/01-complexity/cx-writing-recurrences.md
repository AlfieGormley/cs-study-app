---
id: cx-writing-recurrences
sourceLesson: cx-recurrences
title: Writing recurrences from code
level: advanced
minutes: 2
summary: Separate recursive subproblem costs from each call’s own work.
---

A recurrence describes a recursive call's cost using the costs of its children. Read three things from the code: how many calls it makes, how large their inputs are, and what work remains outside those calls.

## Read the control flow

```python
# a is sorted; lo and hi are inclusive.
def bsearch(a, t, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if a[mid] == t:
        return mid
    if a[mid] < t:
        return bsearch(a, t, mid + 1, hi)
    return bsearch(a, t, lo, mid - 1)
```

Only one branch executes. The function searches one roughly half-size range and does constant outside work, assuming constant-cost indexing, comparisons and index arithmetic. It passes bounds instead of copying a slice.

Merge sort instead solves both halves and merges their results. The merge visits the items in the current range. These different behaviours produce different recurrences:

```formula essential
T_search(n) = T_search(n/2) + Θ(1)
T_merge(n) = 2T_merge(n/2) + Θ(n)
where
T_search(n): binary search's worst-case counted work on n items
T_merge(n): merge sort's counted work on n items
n: the current range length
Θ: a tight growth bound, up to fixed positive multipliers
In words: binary search follows one half with constant outside work; merge sort follows both halves and also processes the whole current range.
```

These are asymptotic models with a fixed positive base-case cost. Half sizes are rounded as the actual ranges require; rounding does not change the stated growth for these algorithms. Binary search is logarithmic, while merge sort is linear times log in the original item count.

Do not count child work twice: the cost assigned to a child already contains everything it does. Conversely, do not forget copying, scanning or combining work in the parent. A function with two calls followed by a full scan has the same cost shape as merge sort even if its purpose is different.

## Key takeaways
- Count executed children, their sizes and outside work separately.
- Include a stopping rule and base-case cost.
- Similar recursion shapes can describe different algorithms.

## Further reading
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
