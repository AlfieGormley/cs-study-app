---
id: sort-merge-memory-runs
title: Merge memory, bottom-up runs and inversions
level: basic
minutes: 2
sourceLesson: sort-merge
summary: Array merging needs an element buffer; linked lists can relink nodes.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Space: the real cost

The array version needs an O(n) auxiliary buffer for merging. You can allocate it once and reuse it, rather than slicing like the teaching code above (which allocates a lot of small lists). The recursion stack adds O(log n).

In-place merge algorithms exist, but they are complicated and slower in practice. This is merge sort's main trade-off against quicksort with smaller-side recursion and heapsort, which need O(log n) and O(1) extra space respectively. Naive quicksort can use O(n) stack space.

**Linked lists** are the exception. Merging two linked lists just re-links nodes, so merge sort on a list needs no buffer, and it does not need random access. It is the standard way to sort a linked list.

## Bottom-up merge sort

You can skip recursion entirely. Treat the array as n runs of length 1, merge neighbouring pairs into runs of length 2, then 4, 8 and so on.

```
width 1: [38][27] [43][3] [9][82] [10]
width 2: [27 38]  [3 43]  [9 82]  [10]
width 4: [3 27 38 43]     [9 10 82]
width 8: [3 9 10 27 38 43 82]
```

Same O(n log n), no recursion stack, and the access pattern is simple sequential passes. It is also the idea behind external sorting.

## A bonus: counting inversions

While merging, whenever you take an element from the right half, it is smaller than every element still waiting in the left half. Each of those is an inversion. Adding `len(left) - i` at that moment counts all inversions in O(n log n), instead of O(n²) by checking every pair. This is used to measure how similar two rankings are (Kendall tau distance).

## Key takeaways
- Array merging needs an element buffer; linked lists can relink nodes.
- Bottom-up merging avoids recursion, and taking a right element counts inversions with remaining left elements.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
