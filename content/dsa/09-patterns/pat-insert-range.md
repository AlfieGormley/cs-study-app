---
id: pat-insert-range
title: Insert a range in three ordered phases
level: intermediate
minutes: 2
sourceLesson: pat-intervals
summary: Copy intervals before the new range, absorb overlaps, then copy the remainder.
---

Here n is the number of valid closed intervals. The input is already sorted by start and internally non-overlapping, so one scan suffices.

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
    # A separate block begins after a gap.
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

## Key takeaways
- Copy intervals before the new range, absorb overlaps, then copy the remainder.
- The linear scan relies on sorted, internally non-overlapping input.
- Unmerged interval pairs are shared unless explicitly copied.

## Further reading
- [Interval cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/interval/)
- [Interval scheduling — Wikipedia](https://en.wikipedia.org/wiki/Interval_scheduling)
- [Activity selection problem — Wikipedia](https://en.wikipedia.org/wiki/Activity_selection_problem)
- [Sweep line algorithm — Wikipedia](https://en.wikipedia.org/wiki/Sweep_line_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
