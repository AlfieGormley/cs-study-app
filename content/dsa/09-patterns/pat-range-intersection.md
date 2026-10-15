---
id: pat-range-intersection
title: Intersect two sorted interval lists
level: intermediate
minutes: 4
sourceLesson: pat-intervals
summary: An intersection begins at the later start and ends at the earlier end.
---

Each input list contains valid closed intervals, sorted by start and internally non-overlapping. Here m and n are the two list lengths.

## Intersecting two sorted lists

For two sorted lists of internally non-overlapping **closed** intervals, keep one current interval from each list. Their shared range begins at the later start and ends at the earlier end. Keep it when its start is no later than its end: a single-point overlap is valid for closed intervals.

```formula
I = [max(a, c), min(b, d)]
I = [max(5, 1), min(10, 5)] = [5, 5]
where
I: the intersection candidate, kept only if its first endpoint is no greater than its second
a: the first interval's start; here 5
b: the first interval's end; here 10
c: the second interval's start; here 1
d: the second interval's end; here 5
max: the larger of two inputs
min: the smaller of two inputs
In words: take the later start and earlier end; closed ranges [5, 10] and [1, 5] share the point 5.
```

Advance whichever interval ends first. That interval cannot meet any later interval in the other list: later intervals start beyond the current one's end. If the two end times tie, advancing either is safe; advancing both is also safe under the strict internal non-overlap contract for closed intervals.

For `A = [[0, 2], [5, 10]]` and `B = [[1, 5], [8, 12]]`, the intersections are `[[1, 2], [5, 5], [8, 10]]`. First advance A past its end at 2, then B past its end at 5, then A past its end at 10. The pointer scan costs O(m + n) time, where m and n are the two list lengths, plus space for the returned intersections.

This is an intersection, not a union: gaps in either input remain gaps in the result. With positive-duration half-open intervals, discard an equal-endpoint candidate because it contains no point.

## Recognising the pattern

| Cue | Approach |
|---|---|
| Merge / union of ranges | Sort by start, extend |
| Insert in a sorted list | Three-phase O(n) |
| Any overlap at all? | Sort, compare neighbours |
| Max simultaneous / rooms | Heap of ends or sweep |
| Keep most / remove fewest | Sort by end, greedy |
| Intersect two sorted lists | Two pointers |

## Pitfalls

- **Unsorted input.** Most algorithms assume sorted by start; sort first unless the problem guarantees it.
- **Inclusive vs exclusive ends.** Decide early, then use `<` or `<=` consistently, including in sweep-line tie-breaks.
- **Forgetting `max` on merge** when one interval contains another.
- **Mutating the caller's list.** `intervals.sort()` sorts in place; use `sorted()` if the caller needs the original.
- **Sorting by the wrong key** in greedy selection: by end, not start or length.

## Recap of the pattern family
- Sort first: after sorting by start, overlaps involve only the current merged block, so one pass suffices.
- Merging extends the last block's end with `max`; insertion into a sorted list is O(n) in three phases.
- Minimum rooms equals peak concurrency: a min-heap of end times or a sweep over +1/−1 events.
- Keep the most non-overlapping intervals by sorting on end time and choosing greedily.
- Pin down closed vs half-open intervals; it decides every comparison and tie-break.

## Key takeaways
- An intersection begins at the later start and ends at the earlier end.
- Advance the interval ending first because it cannot intersect later intervals in the other list.
- Closed intervals can intersect at a single point; do not drop that endpoint.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
