---
id: lin-queue-monotonic-windows
title: Sliding-window maxima with a monotonic deque
level: advanced
minutes: 3
sourceLesson: lin-queues
summary: Remove dominated candidates at the back and expired indices at the front.
---

Use collections.deque from the preceding units. Here n is the input array length and k is a positive window size. The algorithm keeps only candidates that could still become a future maximum, while recording their indices so expiry is testable.

## Monotonic deques: sliding window maximum

Given an array of n numbers and a window size k, find the maximum of every run of k consecutive numbers (each run is a **sliding window**). Recomputing each window from scratch looks at k numbers for each of about n windows, O(nk). A **monotonic deque** does it in O(n).

Keep indices in the deque with their values **decreasing** from front to back. The front is always the current window's maximum.

```python
def window_max(nums, k):
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be >= 1")
    dq, out = deque(), []
    for i, x in enumerate(nums):
        # Older no-larger values cannot win.
        while dq and nums[dq[-1]] <= x:
            # A newer no-smaller value
            # dominates it.
            dq.pop()
        # Keep indices so old candidates
        # expire.
        dq.append(i)
        if dq[0] <= i - k:   # left window
            # Discard the expired front
            # candidate.
            dq.popleft()
        if i >= k - 1:
            # The front remains the window
            # maximum.
            out.append(nums[dq[0]])
    return out

window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
# [3, 3, 5, 5, 6, 7]
```

Values are removed from the **back** when a bigger value arrives (they're dominated: older *and* smaller) and from the **front** when they slide out of the window. Each index enters and leaves once, so the whole run is O(n), the same amortised argument as the monotonic stack.

### Why discarding a candidate is safe

For a three-value window over `[4, 2, 12, 3, 8, 1]`, twelve removes the older four and two from the back. They are smaller and expire earlier, so neither can beat twelve in a future window that still contains them.

Eight later removes three, but twelve stays at the front until its index leaves the window. Only then does eight become the maximum. The four answers are twelve, twelve, twelve and eight. Equal values use the newer index because it remains eligible longer.

The function returns an empty result for empty input or when the requested positive window exceeds the input length: no complete window exists. It rejects zero and negative sizes. Python bool is an int subclass, so True acts like a window of one under this validator. The input must support length, indexing and value comparisons; NaN or a non-total comparison order needs a separately defined policy.

## Key takeaways
- Remove dominated candidates at the back and expired indices at the front.
- Each index enters and leaves at most once.

## Further reading
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
