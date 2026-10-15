---
id: pat-overlap-merge
title: Fix endpoint semantics before merging ranges
level: intermediate
minutes: 5
sourceLesson: pat-intervals
summary: Closed intervals include both endpoints; positive-duration start-inclusive, end-exclusive meetings exclude the end.
---

Interval problems describe things that occupy a range: meetings, bookings, reservations, IP ranges, genome regions, time-series gaps. Each interval is a pair `[start, end]`. Throughout this lesson, n is the number of intervals. The questions are variations on "which ones overlap?", "how many at once?" and "how do I combine them?"

Many interval algorithms begin with **sorting**. For merging, tracking the current merged block makes a linear scan sufficient. Individual intervals can overlap non-neighbours even after sorting (a long interval may contain many others). Other tasks need heaps, trees or even quadratic output when listing every overlapping pair.

## Overlap, precisely

For valid closed intervals `[a, b]` and `[c, d]` (each start no later than its end), the overlap test is:

```formula
a ≤ d and c ≤ b
1 ≤ 6 and 2 ≤ 3
where
a: the start of the first interval
b: the end of the first interval, with a ≤ b
c: the start of the second interval
d: the end of the second interval, with c ≤ d
≤: "is less than or equal to"
In words: two closed intervals overlap exactly when both conditions hold, that is, when each one starts no later than the other ends; the worked line checks [1, 3] against [2, 6], which pass both tests, so they overlap.
```

That is, each starts before (or when) the other ends. The predicate uses two endpoint comparisons, whatever the interval lengths, and works for any ordered values: integers, times or real numbers. It's easier to remember the negation: they do not overlap if either interval ends strictly before the other starts.

> [!warning] Closed or start-inclusive, end-exclusive?
> Do `[1, 3]` and `[3, 5]` overlap? Under the closed interval convention (both ends included), yes: they share the point 3. For meetings, usually no: a meeting ending at 3:00 frees the room for one starting at 3:00. That's a **start-inclusive, end-exclusive** interval `[start, end)`, and for nonempty intervals the test becomes strict (see the formula below). The meeting and scheduling code below assumes positive duration and finite, consistently ordered numeric endpoints. Empty intervals require separate handling. Endpoint semantics affect overlap tests and event ties; merging adjacent half-open intervals is a separate policy, since their union can be consecutive even though they do not overlap.

For half-open intervals the touching case no longer counts:

```formula
a < d and c < b
where
a: the start of the first interval [a, b), included
b: the end of the first interval, excluded, with a < b
c: the start of the second interval [c, d), included
d: the end of the second interval, excluded, with c < d
<: "is strictly less than"
In words: half-open intervals overlap exactly when both conditions hold, that is, only when each starts strictly before the other ends, so a meeting ending at 3:00 and one starting at 3:00 do not clash: for [1, 3) and [3, 5), the check 3 < 3 fails.
```

## Merging overlapping intervals

**Problem.** Merge all overlapping intervals. `[[1,3], [2,6], [8,10], [15,18]]` becomes `[[1,6], [8,10], [15,18]]`.

Sort by start. Walk through, keeping the last merged interval. If the next one starts no later than the last one ends, extend; otherwise start a new one.

```python
def merge(intervals):
    intervals.sort(key=lambda iv: iv[0])
    out = []
    for s, e in intervals:
        if out and s <= out[-1][1]:
            # overlaps: extend the end
            # Containment must not shorten
            # the block.
            out[-1][1] = max(out[-1][1], e)
        else:
            # A separate block begins after
            # a gap.
            out.append([s, e])
    return out
```

```
sorted:  [1,3] [2,6] [8,10] [15,18]
[1,3]    out = [[1,3]]
[2,6]    2 <= 3: extend -> [1,6]
[8,10]   8 > 6: new
[15,18]  15 > 10: new
```

> [!example] Why `max` when extending?
> For `[[1, 10], [2, 3]]`, the second interval is entirely inside the first. Setting the end to `3` instead of `max(10, 3)` would shrink the merged interval: a classic bug.

Why does sorting by start make one pass enough? After sorting, any interval that overlaps the current merged block must start before the block ends, and all such intervals come next in the order. Once you see a start beyond the block's end, no later interval (they all start even later) can touch it.

## Key takeaways
- Closed intervals include both endpoints; positive-duration start-inclusive, end-exclusive meetings exclude the end.
- Sorting by start permits a scan of the current merged block.
- Use the larger end when absorbing a contained interval.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
