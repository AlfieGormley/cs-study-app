---
id: tech-greedy-intervals
title: Greedy choice and interval scheduling
level: intermediate
minutes: 3
sourceLesson: tech-greedy
summary: A locally attractive choice needs a proof of safety.
---

Backtracking tries every option and undoes bad ones. A **greedy algorithm** does the opposite: at each step it makes the choice that looks best *right now*, commits to it, and never reconsiders.

That makes greedy algorithms fast (often just a sort and a single pass) and simple to write. The catch is that "looks best right now" is frequently wrong. The hard part of greedy isn't the code; it's knowing whether the greedy choice is **safe**, and proving it.

## The two properties

A greedy algorithm produces an optimal answer when the problem has:

1. **The greedy choice property**: some optimal solution begins with the greedy choice. Making it never rules out the best answer.
2. **Optimal substructure**: after making the choice, what remains is a smaller instance of the same problem, and an optimal solution to it combines with the choice to give an optimal whole.

Optimal substructure is shared with dynamic programming. The greedy choice property is what lets greedy skip DP's "try every option and take the best": one option is provably enough.

## Interval scheduling

You have one meeting room and a list of requested meetings `(start, end)`. In both interval examples assume finite real endpoints with start < end, representing positive-duration **half-open intervals** [start, end): each meeting includes its start time but not its end time, so a meeting ending at 10 doesn't clash with one starting at 10. Accept as **many** meetings as possible with no overlaps. (In CLRS this is the **activity selection** problem.)

Several greedy rules sound plausible:

| Rule | Works? |
|---|---|
| Earliest start first | No |
| Shortest meeting first | No |
| Fewest conflicts first | No |
| **Earliest finish first** | **Yes** |

Counterexamples kill the wrong rules quickly:

```
Earliest start fails:
  [0-----------------10]
    [1-2] [3-4] [5-6]
  picks 1 meeting; best is 3

Shortest first fails:
  [1-----5]    [6-----10]
        [4--7]
  picks [4,7] alone; best is 2
```

The winning rule: **sort by end time, and take each meeting that starts at or after the last accepted one ends.**

```python
def max_meetings(intervals):
    chosen = []
    last_end = float("-inf")
    by_end = sorted(intervals,
                    key=lambda iv: iv[1])
    for s, e in by_end:
        # Half-open meetings may touch
        # endpoints.
        if s >= last_end:   # compatible
            chosen.append((s, e))
            # Only an accepted meeting
            # changes the boundary.
            last_end = e
    return chosen
```

For n meetings, the sort dominates: **O(n log n)**, and the loop afterwards is a single O(n) pass. The `>=` treats a meeting ending at 10 and one starting at 10 as compatible; use `>` if touching intervals conflict in your problem.

> [!example] Trace
> Meetings sorted by end: (1,4), (3,5), (0,6), (5,7), (3,9), (5,9), (6,10), (8,11), (8,12), (2,14), (12,16).
> - Take (1,4). last_end = 4.
> - (3,5), (0,6) start before 4: skip. Take (5,7). last_end = 7.
> - (3,9), (5,9), (6,10) start before 7: skip. Take (8,11). last_end = 11.
> - (8,12), (2,14) start before 11: skip. Take (12,16).
>
> Result: 4 meetings.

## Key takeaways
- A locally attractive choice needs a proof of safety.
- For maximum meeting count, sort by finish time and accept compatible half-open intervals.

## Further reading
- [Greedy algorithms and Huffman codes — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Python heapq](https://docs.python.org/3/library/heapq.html)
