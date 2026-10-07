---
id: pat-intervals
title: Intervals
level: intermediate
minutes: 13
summary: Sorting intervals to merge and insert them, choosing the most non-overlapping ones greedily, and counting the rooms a schedule needs with a min-heap or a sweep line.
---

Interval problems describe things that occupy a range: meetings, bookings, reservations, IP ranges, genome regions, time-series gaps. Each interval is a pair `[start, end]`. The questions are variations on "which ones overlap?", "how many at once?" and "how do I combine them?"

Many interval algorithms begin with **sorting**. For merging, tracking the current merged block makes a linear scan sufficient. Individual intervals can overlap non-neighbours even after sorting (a long interval may contain many others). Other tasks need heaps, trees or even quadratic output when listing every overlapping pair.

## Overlap, precisely

For valid closed intervals (`a ≤ b`, `c ≤ d`), `[a, b]` and `[c, d]` overlap if and only if

```
a <= d and c <= b
```

i.e. each starts before the other ends. It's easier to remember the negation: they *don't* overlap if one ends before the other starts (`b < c` or `d < a`).

> [!warning] Closed or half-open?
> Do `[1, 3]` and `[3, 5]` overlap? For closed intervals (both ends included), yes: they share the point 3. For meetings, usually no: a meeting ending at 3:00 frees the room for one starting at 3:00. That's a **half-open** interval `[start, end)`, and for nonempty intervals (`a < b`, `c < d`) the test becomes `a < d and c < b`. The meeting and scheduling code below assumes positive duration and finite, consistently ordered numeric endpoints. Empty intervals require separate handling. Endpoint semantics affect overlap tests and event ties; merging adjacent half-open intervals is a separate policy, since their union can be contiguous even though they do not overlap.

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
            out[-1][1] = max(out[-1][1], e)
        else:
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

## Inserting into a sorted list

**Problem.** Given non-overlapping intervals sorted by start, insert a new one, merging as needed.

A generic comparison sort gives an O(n log n) upper bound after appending. Python’s adaptive list sort can exploit the existing run and added interval to take O(n), but this explicit three-phase scan establishes O(n) without depending on sorting adaptivity:

```python
def insert(ivs, new):
    s, e = new
    out, i, n = [], 0, len(ivs)
    # 1. entirely before the new one
    while i < n and ivs[i][1] < s:
        out.append(ivs[i])
        i += 1
    # 2. overlapping: absorb them
    while i < n and ivs[i][0] <= e:
        s = min(s, ivs[i][0])
        e = max(e, ivs[i][1])
        i += 1
    out.append([s, e])
    # 3. entirely after
    out.extend(ivs[i:])
    return out
```

Inserting `[4, 8]` into `[[1,2], [3,5], [6,7], [8,10], [12,16]]`:

```
phase 1: [1,2] ends 2 < 4    keep
phase 2: [3,5]  3 <= 8  -> [3,8]
         [6,7]  6 <= 8  -> [3,8]
         [8,10] 8 <= 8  -> [3,10]
         [12,16] 12 > 10 stop
phase 3: [12,16]
result: [[1,2], [3,10], [12,16]]
```

The returned outer list is new, but unmerged intervals are shared with `ivs`; copy those pairs too if the caller needs independent mutable intervals. Output and slicing use O(n) space.

## Meeting rooms I: any conflict?

"Can one person attend all these meetings?" Sort by start; if any meeting starts before the previous one ends, there's a clash. O(n log n).

```python
def can_attend(meetings):
    meetings.sort()
    for prev, cur in zip(meetings,
                         meetings[1:]):
        if cur[0] < prev[1]:
            return False
    return True
```

## Meeting rooms II: how many rooms?

**Problem.** Given meetings `[start, end)`, find the minimum number of rooms so that no two overlapping meetings share a room. For `[[0,30], [5,10], [15,20]]` the answer is 2.

The answer equals the **maximum number of meetings in progress at any instant**. Two standard ways to find it.

### With a min-heap of end times

Process meetings by start time. The heap holds the last scheduled end time of every room allocated so far, including rooms already free. Its minimum identifies a room whose availability time is earliest.

```python
import heapq

def min_rooms(meetings):
    meetings.sort()          # by start
    ends = []                # min-heap
    for s, e in meetings:
        if ends and ends[0] <= s:
            # earliest room is free: reuse
            heapq.heapreplace(ends, e)
        else:
            heapq.heappush(ends, e)
    return len(ends)
```

```
[0,30]   heap [30]           rooms 1
[5,10]   30 > 5: new room    [10,30]
[15,20]  10 <= 15: reuse     [20,30]
answer: 2
```

O(n log n) time, O(n) space. The heap's size never shrinks, so at the end it equals the peak number of simultaneous meetings. To produce an allocation, extend the heap entries to `(end_time, room_id)` and record each assignment; this end-times-only version returns just the count.

### With a sweep line

Turn each meeting into two events: `+1` at its start and `−1` at its end. Sort the events by time, sweep left to right, and track the running count. The peak is the answer.

```python
def min_rooms_sweep(meetings):
    events = []
    for s, e in meetings:
        events.append((s, 1))
        events.append((e, -1))
    # ties: -1 sorts before +1, so
    # a room frees before it's reused
    events.sort()
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best
```

The tie-break is where the half-open semantics live. Sorting `(time, delta)` tuples puts `(10, -1)` before `(10, 1)`, so a meeting ending at 10 frees its room before one starting at 10 claims it. For closed intervals you'd want starts first.

The sweep line is a difference array (lesson 4) over time, done with sorting instead of an array, so it works for huge or real-valued times. Geometric segment-intersection algorithms also sweep events, but they need additional ordering and intersection logic beyond this concurrency counter.

## Non-overlapping intervals: the greedy choice

**Problem.** Remove the fewest intervals so the rest don't overlap. Equivalently, keep as many as possible: the unweighted **activity selection** problem. Weighted scheduling generally requires a different method, such as dynamic programming.

Sort by **end** time and greedily keep each interval that starts after the last kept one ends. Finishing earliest leaves the most room for everything else; an exchange argument shows no other choice can do better.

```python
def max_non_overlapping(ivs):
    ivs.sort(key=lambda iv: iv[1])
    kept, last_end = 0, float("-inf")
    for s, e in ivs:
        if s >= last_end:     # half-open
            kept += 1
            last_end = e
    return kept   # removals = n - kept
```

Sorting by start instead fails: `[[1, 100], [2, 3], [4, 5]]` would keep `[1, 100]` first and block the other two.

## Recognising the pattern

| Cue | Approach |
|---|---|
| Merge / union of ranges | Sort by start, extend |
| Insert into sorted list | Three-phase O(n) |
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

## Key takeaways
- Sort first: after sorting by start, overlaps involve only the current merged block, so one pass suffices.
- Merging extends the last block's end with `max`; insertion into a sorted list is O(n) in three phases.
- Minimum rooms = peak concurrency: a min-heap of end times or a sweep over +1/−1 events.
- Keep the most non-overlapping intervals by sorting on end time and choosing greedily.
- Pin down closed vs half-open intervals; it decides every comparison and tie-break.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
