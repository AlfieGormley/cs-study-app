---
id: sort-heap-practical-cost
title: Heapsort guarantees and memory locality
level: intermediate
minutes: 3
sourceLesson: sort-heapsort-lower-bound
summary: Iterative heapsort gives constant extra space and a worst-case guarantee.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### Properties

- **In-place**, O(1) extra memory (the iterative sift-down above needs no stack).
- **Worst case O(n log n)**, with no bad inputs to defend against.
- **Not stable.** The root swap sends elements across the array, past their equals.
- **Not adaptive.** A sorted input still costs linear times logarithmic growth (in fact, a sorted ascending array is not a max-heap, so it gets rearranged fully).

### Why it loses to quicksort in practice

On paper heapsort looks strictly better than quicksort. Heapsort can be slower on large arrays, but the ratio depends on implementation, data and hardware. Memory access and comparison counts help explain why:

- Sift-down jumps from index `i` to `2i + 1`. Near the root, frequently reused nodes may remain cached. Deeper in the heap, larger index gaps and less reuse can hurt locality; a different cache line does not by itself imply a cache miss.
- Quicksort's partition scans memory sequentially, which caches and prefetchers love.
- Heapsort also does more comparisons:

```formula
C_heap ≈ 2n log_2(n)
C_quick ≈ 1.39n log_2(n)
where
C_heap: a leading-term scale for the shown ordinary sift-down heapsort on demanding distinct-key inputs; each descent can compare both children, but early stops and duplicates can reduce the count
C_quick: the leading expected comparisons of randomized quicksort with independent uniform pivots on distinct keys
n: the number of elements
log_2(n): the base-2 logarithm of n; about 20 for a million
≈: approximately equal to (leading term only)
In words: heapsort makes roughly 45% more comparisons than randomised quicksort (2 / 1.39 ≈ 1.44), around 40 million versus 28 million for a million elements.
```


So heapsort is used where its guarantees matter more than its speed:

- As the **fallback inside introsort** (C++ `std::sort`, .NET), triggered only when quicksort's recursion goes too deep.
- In the **Linux kernel**, whose `sort()` in `lib/sort.c` is a heapsort: no recursion, no allocation and no worst-case input to exploit.
- In embedded and real-time systems where a fixed upper bound on time and memory matters most.

## Key takeaways
- Iterative heapsort gives constant extra space and a worst-case guarantee.
- Comparison counts and nonsequential access affect speed, so benchmark claims require a workload and hardware.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
