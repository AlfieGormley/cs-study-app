---
id: sort-dual-pivot-contracts
title: Dual pivots and quicksort trade-offs
level: intermediate
minutes: 2
sourceLesson: sort-quicksort
summary: Dual pivots change comparisons and swaps; an analytic model does not prove a runtime improvement.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Variants in production

- **Dual-pivot quicksort** (Yaroslavskiy, 2009) partitions into three parts using two pivots. Java has used it for `Arrays.sort` on primitive arrays since Java 7. For the analysed unsampled algorithm on uniformly random distinct keys, it makes about 5% fewer comparisons than classic quicksort but more swaps. That model alone does not establish a runtime or cache-miss improvement for a modern Java implementation. The current JDK implementation also tracks recursion depth and falls back to heapsort, and the Java documentation describes it as O(n log n) on all data sets.

```formula reference
C_dual ≈ 1.9n ln(n)
C_classic ≈ 2n ln(n)
where
C_dual: the expected comparisons of Yaroslavskiy's dual-pivot quicksort (leading term)
C_classic: the expected comparisons of classic single-pivot quicksort (leading term)
n: the number of elements, distinct and in uniformly random order
ln(n): the natural logarithm of n (base e, about 2.718)
≈: approximately equal to, keeping only the leading term
In words: dual-pivot quicksort makes about 5% fewer comparisons in this model.
```

- **Not stable.** Partitioning swaps elements over long distances, so equal keys can be reordered. That is why Java uses quicksort only for primitives (where stability is invisible) and a merge sort for objects.

## Summary

| | Quicksort |
|---|---|
| Average time | Θ(n log n) expected |
| Worst time | Θ(n²) (introsort: n log n) |
| Extra space | O(log n) stack with smaller-side recursion |
| Stable | No |

## Key takeaways
- Dual pivots change comparisons and swaps; an analytic model does not prove a runtime improvement.
- Objects with visible ties need a stable sort; quicksort partitioning normally reorders ties.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
- [Analysis of Yaroslavskiy’s dual-pivot quicksort](https://arxiv.org/abs/1310.7409)
