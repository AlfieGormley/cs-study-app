---
id: cx-constants-locality
sourceLesson: cx-in-practice
title: Constants, locality and theoretical winners
level: advanced
minutes: 5
summary: Explain practical performance differences hidden by asymptotic labels.
---

Here n is the input size unless an example names another dimension. The asymptotic model leaves out factors that must be measured on the actual workload.

## Constant factors

Big-O hides constants, but the computer doesn't. Two algorithms in the same class can differ by 10x, and an asymptotically worse one can win for all inputs you'll ever see.

The standard example is sorting small arrays. Insertion sort is Θ(n^2), but its inner loop is tiny, branch-predictable and works entirely in cache. For small n it beats merge sort and quicksort, so real libraries use **hybrid sorts**:

- **Timsort-style natural merge sorts** extend short runs with binary insertion sort, then merge them. Thresholds differ by implementation; modern CPython uses a Powersort merge policy, so a single threshold/policy should not be attributed to both Python and Java.
- **Introsort** (C++ `std::sort` in common implementations) runs quicksort, switches to heapsort if the recursion gets too deep (guaranteeing O(n log n) worst case), and leaves small partitions (16 elements in libstdc++) for a final insertion sort pass.

The general lesson: the crossover point is found by measurement, not theory.

## The memory hierarchy

The RAM model treats memory accesses uniformly, but real machines have caches, main memory and storage with different access costs.

> [!note] Content gap: hardware latency measurements
> The repository contains no reproducible measurement setup for the original latency table. Exact nanosecond and microsecond figures are omitted; consult the target hardware documentation and benchmark its access patterns. Cache-line size is hardware-specific (64 bytes is common on x86; ARM implementations vary).

So **access patterns** matter enormously:

- **Arrays vs linked lists.** Summing an array and summing a linked list are both Θ(n). But the array is contiguous: a 64-byte cache line holds eight 8-byte values and the prefetcher streams the rest. A linked list's nodes can be scattered across memory, and each `next` pointer must be loaded before the following address is known, so ordinary demand loads form a dependency chain and are harder to overlap. The list is often several times slower, and much worse when nodes are scattered.
- **Traversal order.** C stores 2D arrays row by row. For an N by N array of 8-byte values, both loops below are Θ(N^2), touching all N × N elements once:

```c
/* row order: sequential */
/* j changes fastest: stay in one row. */
for (i = 0; i < N; i++)
    for (j = 0; j < N; j++)
        sum += a[i][j];

/* column order: N*8-byte jumps */
/* i changes fastest: visit each row. */
for (j = 0; j < N; j++)
    for (i = 0; i < N; i++)
        sum += a[i][j];
```

For large N (so the matrix doesn't fit in cache), the column-order loop touches a new cache line on almost every access and can be several times slower, sometimes by an order of magnitude.

This is why B-trees, with hundreds of keys per node, beat binary search trees for databases and file systems: they need far fewer memory or disk accesses for the same Θ(log n) search. Cache-aware and **cache-oblivious** algorithms are designed around counting cache misses instead of instructions.

## Galactic algorithms

Some algorithms have the best known asymptotic complexity but are never used, because their constants are astronomical. They're nicknamed **galactic algorithms**: they would only win on inputs larger than anything that fits on Earth.

- **Matrix multiplication.** For n by n matrices, the naive algorithm is Θ(n^3) and Strassen's is about Θ(n^2.807). Theoretical algorithms descending from Coppersmith–Winograd have pushed the exponent below 2.372, but they are useless in practice. Even Strassen is used only above a size threshold, if at all; optimised BLAS libraries mostly rely on carefully blocked Θ(n^3) code that uses the cache brilliantly.
- **Integer multiplication.** For n-digit numbers, Harvey and van der Hoeven's 2019 algorithm runs in O(n log n), believed optimal, but only beats existing methods for astronomically large numbers. Practical libraries such as GMP switch between schoolbook, Karatsuba, Toom–Cook variants and FFT-based multiplication at tuned size thresholds.

The opposite trap also exists: assuming a fancy algorithm is needed when the simple one, with a good constant, is fast enough.

## Key takeaways
- Constant factors and memory access patterns can determine measured performance.
- Sequential array traversal has better locality than scattered dependent accesses.
- An asymptotically better algorithm may have constants that make it impractical.

## Further reading
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Galactic algorithm — Wikipedia](https://en.wikipedia.org/wiki/Galactic_algorithm)
- [Introsort — Wikipedia](https://en.wikipedia.org/wiki/Introsort)
- [Timsort — Wikipedia](https://en.wikipedia.org/wiki/Timsort)
