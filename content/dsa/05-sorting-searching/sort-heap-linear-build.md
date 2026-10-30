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

Inserting n elements one at a time would cost O(n log n) in the worst case. The bottom-up build is cheaper because most nodes are near the bottom, where sift-down is short. About half the nodes are leaves (cost 0), a quarter are one level up (cost at most 1), an eighth cost at most 2, and so on. Lots of very short moves at the bottom and a few long ones at the top add up to fewer swaps than there are elements:

```formula reference
W < n(1/2 + 1/4 + 1/8 + …) = n
where
W: the total number of sift-down swaps the bottom-up build can make
n: the number of elements in the heap
1/2, 1/4, 1/8: at most these fractions of the n nodes can move down at least one, two and three levels
…: "and so on": the fractions keep halving
In words: at most half the nodes can move down even one level, at most a quarter two levels, at most an eighth three, and those halving counts add up to fewer swaps than there are nodes.
```

So building the heap is O(n). For a million elements that is at most about a million swaps, not 20 million. The extraction phase then does one sift-down per extracted element, each costing O(log n), so heapsort overall is **Θ(n log n) in the worst case**.

## Key takeaways
- Most heap nodes have short or zero sift-down paths.
- Bottom-up construction is linear although separate insertions have a logarithmic worst-case cost each.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
