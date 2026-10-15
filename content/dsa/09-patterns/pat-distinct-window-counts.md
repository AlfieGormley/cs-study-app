---
id: pat-distinct-window-counts
title: Count exactly a distinct-value budget
level: intermediate
minutes: 4
sourceLesson: pat-sliding-window
summary: Every valid start between the left and right edges contributes one ending window.
---

Here n is the input length and k is an integer distinct-value budget. Values must be hashable; count-map operations have expected constant cost.

## Counting windows: the at-most trick

"Count subarrays with **exactly** k distinct values" is awkward for a window: removing an element can keep the count at k or drop it, so there's no single clean shrink rule. But "**at most** k" is monotonic. For each `hi`, after shrinking, every window ending at `hi` and starting anywhere in `[lo, hi]` qualifies: that's `hi - lo + 1` windows.

```python
def at_most(a, k):
    if type(k) is not int:
        raise ValueError("integer k")
    if k < 0:
        return 0
    count = {}
    lo = total = 0
    for hi, x in enumerate(a):
        # Include the new value in the count
        # map.
        count[x] = count.get(x, 0) + 1
        while len(count) > k:
            count[a[lo]] -= 1
            if count[a[lo]] == 0:
                # Zero counts must not
                # inflate distinctness.
                del count[a[lo]]
            lo += 1
        # Every surviving start gives one
        # subarray.
        total += hi - lo + 1
    return total

def exactly(a, k):
    return at_most(a, k) - at_most(a, k - 1)
```

These functions count nonempty subarrays; a negative distinct budget gives 0, and `exactly(a, 0)` gives 0. Values must be hashable.

The subtraction works because every subarray with at most k distinct values has either exactly k or at most k − 1:

```formula
E(k) = M(k) − M(k − 1)
E(2) = M(2) − M(1) = 12 − 5 = 7
where
E(k): the number of nonempty subarrays with exactly k distinct values (`exactly(a, k)`)
M(k): the number with at most k distinct values (`at_most(a, k)`)
k: the number of distinct values asked for, a whole number
In words: count everything with at most k distinct values, then take away everything with at most k − 1; what is left has exactly k.
```

For `[1, 2, 1, 2, 3]` with k = 2: twelve subarrays have at most two distinct values (all 15 except the three that end with 3 and also contain both 1 and 2), and five have at most one (the five single elements, since no two neighbours are equal). So exactly 7 subarrays have exactly two distinct values.

## Recognising the pattern

| Cue | Kind of window |
|---|---|
| "every k consecutive" | Fixed |
| "longest ... such that" | Variable, shrink when invalid |
| "shortest ... containing" | Variable, shrink while valid |
| "count subarrays at most k" | Variable, add `hi-lo+1` |
| "exactly k" | Subtract two at-most counts |
| Max/min of each window | Monotonic deque (the monotonic stack and deque units) |
| Sum equals k, negatives allowed | Not a window: prefix sums |

## Pitfalls

- **Non-contiguous sequence problems.** "Subsequence" means elements need not be adjacent; a contiguous window alone does not enumerate arbitrary subsequences. DP, greedy or other methods may apply.
- **Negative numbers** break sum-based windows, as above.
- **Recording at the wrong time.** For "longest", record after shrinking (window valid). For "shortest", record *inside* the shrink loop before removing.
- **Expensive validity checks.** Keep a counter (`missing`, `len(count)`) so each check is O(1).
- **Stale map entries.** Delete keys whose count hits 0, or `len(count)` overstates the distinct count.

## Recap of the pattern family
- A sliding window maintains a contiguous range's summary incrementally, turning O(n²) or O(n × k) into O(n), where n is the input length and k the window size.
- Each element enters and leaves the window no more than once, so the inner `while` doesn't make it quadratic.
- Variable windows need monotonic validity; negative numbers usually break sum conditions.
- "Longest" shrinks until valid then records; "shortest" records while shrinking a valid window.
- Count exactly a budget by subtracting the at-most-previous-budget count from the at-most-budget count.

## Key takeaways
- Every valid start between the left and right edges contributes one ending window.
- Subtract the at-most-lower-budget count from the at-most-budget count.
- Delete zero-count map keys; these examples count nonempty subarrays.

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
