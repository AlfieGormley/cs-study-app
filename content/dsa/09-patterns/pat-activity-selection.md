---
id: pat-activity-selection
title: Keep the most compatible activities
level: intermediate
minutes: 2
sourceLesson: pat-intervals
summary: Choose the compatible activity that finishes earliest.
---

Here n is the number of positive-duration half-open intervals. Touching endpoints are allowed; minimise removals by maximising the number retained.

## Non-overlapping intervals: the greedy choice

**Problem.** Remove the fewest intervals so the rest don't overlap. Equivalently, keep as many as possible: the unweighted **activity selection** problem. Weighted scheduling generally requires a different method, such as dynamic programming.

Sort by **end** time and greedily keep each interval that starts after the last kept one ends. Finishing earliest leaves the most room for everything else; an exchange argument shows no other choice can do better.

```python
def max_non_overlapping(ivs):
    ivs.sort(key=lambda iv: iv[1])
    kept, last_end = 0, float("-inf")
    for s, e in ivs:
        # Touching endpoints are allowed.
        if s >= last_end:
            kept += 1
            # The earliest finish leaves
            # most room.
            last_end = e
    return kept   # removals = n - kept
```

Sorting by start instead fails: `[[1, 100], [2, 3], [4, 5]]` would keep `[1, 100]` first and block the other two.

## Why replacing the first choice is safe

Take an optimal compatible schedule and compare its first interval with the earliest-finishing interval. Replacing that first choice with the earliest-finishing one leaves no later finish time, so every later selected interval remains compatible. The replacement keeps the same number of intervals. Apply the argument again to the intervals that can start after that finish.

This is a statement about unweighted counts and positive-duration half-open intervals. An early-finishing interval with a small reward need not belong to an optimal weighted interval schedule, whose objective is total reward rather than interval count. The algorithm sorts in O(n log n) time and scans in O(n), where n is the interval count. The scan uses constant extra state; Python’s in-place sort may still allocate linear temporary storage.

## Key takeaways
- Choose the compatible activity that finishes earliest.
- An exchange argument supports the greedy choice for unweighted activity counts.
- Weights change the objective and generally require a different method.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Princeton activity-selection exchange argument](https://www.cs.princeton.edu/courses/archive/spring18/cos423/lectures/04GreedyAlgorithmsI-2x2.pdf)
