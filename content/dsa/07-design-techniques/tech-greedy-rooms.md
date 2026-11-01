---
id: tech-greedy-rooms
title: Minimum rooms by earliest availability
level: intermediate
minutes: 2
sourceLesson: tech-greedy
summary: Process meetings by start time and reuse the earliest-free room.
---

Accepting a maximum subset is different from assigning every meeting a room. Keep the previous unit’s positive-duration half-open interval convention. Here n is the number of meetings, and touching endpoints permit room reuse.

## Interval partitioning: minimum rooms

Now every meeting *must* happen. What's the minimum number of rooms?

Greedy: process meetings by **start** time, and put each one in any room that has become free; open a new room only if none has. A **min-heap** of room end times finds the earliest-free room in O(log n) for n meetings.

```python
import heapq

def min_rooms(intervals):
    ends = []               # min-heap
    for s, e in sorted(intervals):
        # The earliest-free room can be
        # reused now.
        if ends and ends[0] <= s:
            # Keep one finish time per
            # allocated room.
            heapq.heapreplace(ends, e)
        else:
            heapq.heappush(ends, e)
    return len(ends)
```

Why is it optimal? The number of meetings running at the same moment is a hard lower bound: they each need their own room. If three meetings are all running at 10:15, no schedule can manage with fewer than three rooms.

```formula reference
R_min ≥ D
D = max_t m(t)
where
R_min: the minimum number of rooms any valid schedule needs
D: the depth: the most meetings that overlap at any single moment
t: a moment in time
m(t): the number of meetings in progress at moment t
max_t: the largest value over all moments t
≥: is at least
In words: the minimum number of rooms is at least the largest number of meetings in progress at any single moment.
```

Greedy opens another room only when every room already allocated is busy at the new meeting’s start. The number of simultaneous meetings then equals the room count, so that count cannot exceed the maximum overlap. It therefore matches the lower bound, in O(n log n) time for n meetings. The same pattern fits any pool of identical reusable resources, such as machines or worker slots, when every job must be served and a resource can be reused once its current job ends.

## Key takeaways
- Process meetings by start time and reuse the earliest-free room.
- Maximum simultaneous overlap is a lower bound that the heap algorithm meets.

## Further reading
- [Greedy algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Python heapq](https://docs.python.org/3/library/heapq.html)
