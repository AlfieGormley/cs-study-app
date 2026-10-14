---
id: sort-heap-linear-build
title: Why heap construction is linear
level: intermediate
minutes: 2
sourceLesson: sort-heapsort-lower-bound
summary: Most heap nodes have short or zero sift-down paths.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### Why the build phase is O(n), not O(n log n)

Inserting n elements one at a time would cost O(n log n). The bottom-up build is cheaper because most nodes are near the bottom, where sift-down is short. About half the nodes are leaves (cost 0), a quarter are one level up (cost at most 1), an eighth cost at most 2, and so on:

```formula
W ≤ Σ_h ⌊n / 2^h⌋
W < n
where
W: the total number of sift-down swaps the bottom-up build can make
n: the number of elements in the heap
h: the number of edges in a longest downward path from a node to a descendant leaf (zero for a leaf)
Σ_h: sum the following term over all integer heights h of at least one
⌊ ⌋: floor, round down to an integer
2^h: two raised to the height h; there are at most floor(n / 2^h) nodes with height at least h
<: strictly less than
≤: less than or equal to
In words: count one possible swap for each level a node could descend; the number of nodes reaching each level halves, so the total is strictly below the number of elements for a nonempty heap.
```

The corresponding geometric series of one half, one quarter, one eighth and so on sums to one, so building the heap is O(n). For a million elements that is at most about a million swaps, not 20 million. The extraction phase does one fewer sift-down than the input size of O(log n) each, so heapsort overall is **Θ(n log n) in the worst case**.

## Key takeaways
- Most heap nodes have short or zero sift-down paths.
- Bottom-up construction is linear although separate insertions have a logarithmic worst-case cost each.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
