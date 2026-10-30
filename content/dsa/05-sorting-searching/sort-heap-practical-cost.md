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
- Heapsort also does more comparisons: the ordinary sift-down shown here compares both children at almost every level on the way down. Run on a million shuffled distinct keys, the heapsort code from the extraction unit made about 37 million comparisons, roughly 1.5 times the 25 million that randomised quicksort makes on average. The leading terms below suggest a slightly smaller ratio, about 1.44; lower-order terms still matter at practical sizes.

```formula reference
C_heap ≈ 2n log_2(n)
C_quick ≈ 1.39n log_2(n)
where
C_heap: the leading term of the comparisons the ordinary sift-down heapsort shown here makes on large random distinct keys; each descent compares both children at almost every level, and lower-order terms reduce the count at practical sizes (about 1.85n log_2(n) measured at a million keys)
C_quick: the leading term of the expected comparisons of randomised quicksort with independent uniform pivots on distinct keys
n: the number of elements
log_2(n): the base-2 logarithm of n; about 20 for a million
≈: approximately equal to (leading term only)
In words: by leading terms alone, ordinary heapsort makes about 1.44 times as many comparisons as randomised quicksort on large random inputs; at a million keys the measured ratio is about 1.5.
```

> [!analogy] Real-world analogy: fetching books along one aisle or across storeys
> Fetching books from one aisle in shelf order is quick: you walk along and pick each one up. Fetching books whose shelf numbers keep doubling (shelf 1, then 3, then 7, then 15) soon sends you to another storey for every book, even though you fetch no more books.
>
> **How it maps:** walking along one aisle is quicksort's sequential partition scan, which caches and prefetchers handle well. The doubling shelf numbers are a sift-down path from index `i` to `2i + 1`, whose jumps grow as it goes deeper.
>
> **Where it stops:** the first few shelves near the start are visited so often that they stay "at hand" (the top heap levels stay cached), and a far jump does not always cost a cache miss. The real slowdown depends on the data size and the machine, so it has to be measured.


So heapsort is used where its guarantees matter more than its speed:

- As the **fallback inside introsort** (C++ `std::sort`, .NET), triggered only when quicksort's recursion goes too deep.
- In the **Linux kernel**, whose `sort()` in `lib/sort.c` is a heapsort: no recursion, no allocation and no worst-case input to exploit. It uses a "bottom-up" sift-down variant that, according to its source comments, needs a bit more than half as many comparisons on average as checking both children at every level.
- In embedded and real-time systems where a fixed upper bound on time and memory matters most.

## Key takeaways
- Iterative heapsort gives constant extra space and a worst-case guarantee.
- Comparison counts and nonsequential access affect speed, so benchmark claims require a workload and hardware.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
