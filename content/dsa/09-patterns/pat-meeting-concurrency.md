---
id: pat-meeting-concurrency
title: Count rooms with end times or events
level: intermediate
minutes: 4
sourceLesson: pat-intervals
summary: A room-count heap retains one last end time per allocated room.
---

Here n is the number of positive-duration, start-inclusive, end-exclusive meetings with finite consistently ordered endpoints. A room is reusable at exactly its previous end time. The Recursion, Backtracking & Greedy module's "Minimum rooms by earliest availability" unit proves why the heap method below is optimal; this unit compares it with the sweep line.

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
            # The earliest-free room is
            # free by now: reuse it.
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
    # At equal times (e, -1) sorts
    # before (s, 1): a room frees
    # before it is reused.
    events.sort()
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best
```

The tie-break is where the start-inclusive, end-exclusive semantics live. Sorting `(time, delta)` tuples puts `(10, -1)` before `(10, 1)`, so a meeting ending at 10 frees its room before one starting at 10 claims it. For closed intervals you'd want starts first.

> [!analogy] Real-world analogy: a clicker counter at a venue door
> A steward at the only door clicks up when someone comes in and down when someone leaves. The highest number the clicker ever shows is the peak attendance. If one person leaves at exactly the moment another arrives, the steward counts the exit first, so the venue never seems to hold one person too many.
>
> **How it maps:** each meeting start is a +1 click and each end is a −1 click; sorting the events puts the clicks in time order; `cur` is the clicker and `best` its highest reading, which is the number of rooms needed. Counting exits first at equal times is the `(time, -1)` before `(time, 1)` tie-break for start-inclusive, end-exclusive meetings.
>
> **Where it stops:** the steward counts people as they happen; the algorithm needs all the events up front so it can sort them. The peak tells you how many rooms are needed, not which meeting goes in which room; producing those room assignments needs the heap version extended to record a room for each meeting.

The sweep line is a difference array (the prefix-sum units) over time, done with sorting instead of an array, so it works for huge or real-valued times. Geometric segment-intersection algorithms also sweep events, but they need additional ordering and intersection logic beyond this concurrency counter.

## A bounded integer timeline

If every start and end is an integer minute in a known day, allocate one difference slot for each boundary. Add one at a start and subtract one at an end, then sweep the slots with a running sum. Aggregating all changes at the same boundary respects start-inclusive, end-exclusive semantics. The maximum running count is the room requirement.

This takes O(n + T) work and O(T) slots, where T is the largest permitted integer boundary and n is the number of meetings. A 1,440-minute day needs 1,441 boundary slots when the final end is included in the sweep. Arbitrary real-valued times instead use sorted events or another ordered representation.

## Key takeaways
- A room-count heap retains one last end time per allocated room.
- For start-inclusive, end-exclusive meetings, process end events before start events at equal times.
- A bounded integer timeline allows a difference-array scan without sorting.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
