---
id: sort-simple-production
title: Choosing simple sorts in production
level: basic
minutes: 3
sourceLesson: sort-simple
summary: Compare writes, comparisons and existing order before choosing a simple sort.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Comparison

| Sort | Comparisons | Swaps/writes | Stable? |
|---|---|---|---|
| Bubble | O(n²), O(n) if sorted | One per inversion | Yes |
| Selection | Fixed quadratic count | At most one swap per pass | No |
| Insertion | O(n + I) | One per inversion | Yes |

Here n is the number of elements and I the number of inversions in the input. The exact selection comparison and swap bounds are:

```formula
C = (n(n − 1)) / 2
S ≤ n − 1
where
C: number of key comparisons
S: number of swaps, counting self-swaps
n: number of input elements; assume at least one
≤: less than or equal to
In words: Selection scans every remaining candidate and performs no more than one swap per nonfinal position.
```

All three are in-place with O(1) extra space and O(n²) average and worst case.

## Where these appear in real systems

- **Hybrid sorts.** Timsort (Python, Java objects, V8) extends short runs with binary insertion sort. C++'s `std::sort` in libstdc++ finishes with insertion sort over the nearly sorted array that introsort leaves behind. pdqsort switches to insertion sort for partitions below about 24 elements.
- **Nearly sorted data.** Maintaining a sorted list with occasional appends, or re-sorting a leaderboard after a few scores change, is close to O(n) with insertion sort.
- **Shell sort** generalises insertion sort by first sorting elements far apart (gaps like 701, 301, 132, ... 1), removing many inversions with each long move. It is still used in some embedded code because it is tiny and needs no recursion.

## Pitfalls

1. **Breaking stability by accident.** Using `>=` instead of `>` in bubble or insertion sort silently makes them unstable. Stability is a property of the implementation, not just the algorithm's name.
2. **Assuming "simple" means "fine for small inputs" without measuring what small is.** With 10,000 elements, a quadratic sort makes about 50 million comparisons (10,000 × 10,000 / 2). **Content gap:** cross-language millisecond/second timings are omitted because no reproducible benchmark, hardware or implementation was supplied.
3. **Judging by comparisons alone.** On 10,000 reversed elements, selection sort and insertion sort both make about 50 million comparisons, but insertion sort also does about 50 million writes while selection sort does at most 9,999 swaps. Which is cheaper depends on what your "write" costs.

## Key takeaways
- Compare writes, comparisons and existing order before choosing a simple sort.
- Hybrid sorts use insertion sort for small ranges, but the threshold requires measurement.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
