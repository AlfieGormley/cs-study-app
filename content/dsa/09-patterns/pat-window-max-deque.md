---
id: pat-window-max-deque
title: Discard dominated values and expire old indices
level: advanced
minutes: 3
sourceLesson: pat-monotonic
summary: Keep decreasing candidate values so the front answers the current maximum.
---

Here n is the array length and k is an integer window length from one to n. A deque supports removals at both ends. The Arrays, Lists, Stacks & Queues module's monotonic-deque unit introduces this structure; this unit places it among the window and stack patterns and traces its two kinds of removal.

## Monotonic deque: sliding window maximum

**Problem.** Return the maximum of every window of size `k`.

A heap with only lazy deletion of expired roots can retain O(n) entries and take O(n log n). A bounded indexed heap or periodic rebuilding can instead give O(n log(k + 1)). A **monotonic deque** gives O(n).

Keep indices in a deque whose values are **decreasing** from front to back. The front is always the current window's maximum.

- **Push at the back:** before adding `i`, pop smaller-or-equal values from the back. They need not represent any future maximum: `a[i]` is at least as large and expires later. Equal maxima are interchangeable when returning only values.
- **Expire at the front:** if the front index has slid out of the window, pop it.

```python
from collections import deque

def window_max(a, k):
    if (type(k) is not int
            or not 1 <= k <= len(a)):
        raise ValueError("1 <= k <= len(a)")
    dq = deque()  # values decrease
    out = []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            # Newer no-smaller value lasts
            # longer.
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            # Expire a position outside this
            # window.
            dq.popleft()
        if i >= k - 1:
            # The surviving front is the
            # maximum.
            out.append(a[dq[0]])
    return out
```

```
a = [1, 3, -1, -3, 5, 3, 6, 7], k = 3

i  x   deque (values)   out
0  1   [1]
1  3   [3]
2  -1  [3,-1]           3
3  -3  [3,-1,-3]        3
4  5   [5]              5
5  3   [5,3]            5
6  6   [6]              6
7  7   [7]              7
```

Result `[3, 3, 5, 5, 6, 7]`, one value per full window: the first window ends at index 2 and the last at index 7, so 8 values in windows of 3 give 6 maxima.

Each index enters and leaves the deque once: O(n) time, O(k) auxiliary space, plus O(n − k + 1) output space.

The same structure powers DP optimisations where `dp[i]` depends on the max or min of `dp` over a sliding range (for example "jump game VI"). A related dominance argument solves "shortest subarray with sum at least k" with negative values, using a deque of increasing prefix sums; that is not simply the same fixed-range DP recurrence.

## Key takeaways
- Keep decreasing candidate values so the front answers the current maximum.
- A newer no-smaller value dominates an older value for future windows.
- Expire candidates by position and count the separate returned-output storage.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
