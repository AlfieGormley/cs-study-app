---
id: sort-merge-choosing
title: Choosing and improving merge sort
level: basic
minutes: 2
sourceLesson: sort-merge
summary: Merge sort provides stable ordering and a worst-case guarantee.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Trade-offs and pitfalls

| Property | Merge sort |
|---|---|
| Time (all cases) | Θ(n log n) |
| Extra space | O(n) for arrays |
| Stable | Yes, with `<=` |
| Adaptive | No (plain version) |

- **Use it when** you need guaranteed linear times logarithmic growth, stability, a linked list, or data on disk or arriving as sorted streams.
- **Small sub-arrays.** Recursing down to size 1 wastes time. Real implementations switch to insertion sort for small pieces, at a threshold chosen by benchmarking: libstdc++'s `std::stable_sort` insertion-sorts chunks of 7 elements when it can allocate a merge buffer, and CPython's list sort extends short runs to a minimum of 32 to 64 elements.
- **Skip merges that are not needed.** If `left[-1] <= right[0]`, the halves are already in order and the merge can be skipped. For an index-range implementation that returns without copying an already ordered range, this makes sorted-input time linear. In the slicing example, creating and concatenating halves still costs Θ(n log n), even if comparisons become linear.
- **Midpoint overflow.** In languages with fixed-width integers, `(lo + hi) / 2` can overflow on huge arrays. Use `lo + (hi - lo) / 2`. This bug sat in Java's library for years (covered later in this module).

## Key takeaways
- Merge sort provides stable ordering and a worst-case guarantee.
- Skipping comparisons in a slicing implementation still leaves copying costs.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
