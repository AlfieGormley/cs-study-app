---
id: pat-window-validity
title: Choose a valid grow-and-shrink rule
level: intermediate
minutes: 3
sourceLesson: pat-sliding-window
summary: Longest-window validity must survive taking subwindows; shortest covering validity must survive expansion.
---

A variable window changes length to restore or preserve a predicate. Here n is the input length. A subarray or substring occupies a contiguous range; an arbitrary subsequence may skip positions.

## Variable-size windows

Here the window grows and shrinks. The template:

```python
lo = 0
for hi in range(len(a)):
    add(a[hi])                 # grow right
    # This partial template repairs
    # validity.
    while not valid():
        remove(a[lo])          # shrink left
        lo += 1
    record(hi - lo + 1)    # valid now
```

`hi - lo + 1` is the window's length, because both ends are included:

```formula
L = hi − lo + 1
L = 5 − 3 + 1 = 3
where
L: the number of elements in the window a[lo..hi]
lo: the index of the window's first element
hi: the index of the window's last element
In words: a window from index 3 to index 5 holds positions 3, 4 and 5, three elements; forgetting the + 1 is a classic off-by-one bug.
```

If the empty window is valid and add/remove/valid/record each cost O(1), both pointers only move forwards, so each element is added once and removed no more than once: **O(n) total**, even with the inner `while`. That amortised argument is the reason the pattern is fast.

> [!warning] The precondition: monotonicity
> These variable-window templates need **monotonic** validity: every subwindow of a valid window stays valid for the longest/shrink-when-invalid template; every superwindow of a valid window stays valid for the shortest/shrink-while-valid template. Merely being able to make some invalid window valid by growing is insufficient. "Sum at most k", with non-negative numbers and a non-negative limit k, qualifies. With **negative numbers**, removing an element can *increase* the sum, so the window can't tell which way to move. Use prefix sums instead (the prefix-sum units).

## When to record a candidate

For a longest valid window, shrink until validity is restored, then record its length. Typical downward-closed predicates are at most a specified number of distinct values, at most a specified number of zeros, or a sum at most a nonnegative limit when all values are nonnegative. For products of integers at least one and a limit greater than one, removing values cannot increase the product; the same longest/counting shape is valid.

For a shortest window whose positive values sum to at least a positive target, expansion cannot destroy validity. Once valid, record a candidate **inside** the shrink loop, then remove from the left. Stop shrinking when the sum falls below target. Each endpoint still moves only forwards. For `[2, 3, 1, 2, 4, 3]` with target 7, the final `[4, 3]` is the shortest qualifying range.

A negative value can rescue an earlier sum that looked too large. For `[3, -2, 1]` with a limit of 2, removing the initial 3 immediately loses the valid whole-array answer. Use a prefix-based method that retains the needed starts instead.

For counting under a downward-closed predicate, keep the smallest valid left edge. Every starting position from that edge through the current right edge then gives a valid ending subarray. Adding the number of such starts counts those subarrays once.

## Key takeaways
- Longest-window validity must survive taking subwindows; shortest covering validity must survive expansion.
- With constant-cost updates, forward-only endpoints give linear total work.
- Negative values can break monotone sum rules; consecutive positions alone does not prove a window solution.

## Further reading
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [String cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/string/)
- [Two pointers — USACO Guide](https://usaco.guide/silver/two-pointers)
