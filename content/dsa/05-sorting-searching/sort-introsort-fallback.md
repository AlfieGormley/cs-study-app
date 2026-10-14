---
id: sort-introsort-fallback
title: Introsort and adversarial inputs
level: intermediate
minutes: 2
sourceLesson: sort-quicksort
summary: A depth budget detects excessive quicksort work and switches to heapsort.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Introsort: a worst-case guarantee

David Musser's **introsort** (1997) combines three algorithms:

1. Run quicksort (median-of-three pivots).
2. Track recursion depth. If it exceeds a limit (formula below), the pivots are going badly, so switch that sub-array to **heapsort**, which is O(n log n) worst case (covered later in this module).
3. Leave sub-arrays below a threshold (16 elements in libstdc++) unsorted, then finish with insertion sort.

The depth limit in libstdc++ is:

```formula
d_max = 2⌊log_2(n)⌋
d_max = 2 × ⌊log_2(10^6)⌋ = 2 × 19 = 38
where
d_max: the recursion depth at which introsort gives up on quicksort for that sub-array
n: the number of elements being sorted; here a million (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.93
⌊ ⌋: the floor: round down to a whole number, so ⌊19.93⌋ = 19
In words: introsort allows about twice the depth that perfect halving would need before deciding the pivots are bad.
```

Since heapsort costs O(n log n) on any sub-array it takes over, the total stays O(n log n). You get quicksort's speed in the common case and an O(n log n) guarantee. C++ requires `std::sort` to be O(n log n) in the worst case since C++11, and the major standard libraries (libstdc++, MSVC and current libc++) use introsort-style hybrids. .NET's `Array.Sort` is introsort too. pdqsort (covered later in this module) is a modern descendant.

## Key takeaways
- A depth budget detects excessive quicksort work and switches to heapsort.
- Deterministic pivot heuristics alone cannot guarantee safety against adversarial inputs.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
