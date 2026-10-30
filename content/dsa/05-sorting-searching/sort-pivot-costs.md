---
id: sort-pivot-costs
title: Pivot choices and quadratic inputs
level: intermediate
minutes: 4
sourceLesson: sort-quicksort
summary: Consistently extreme pivots make a quadratic triangle of comparisons.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Pivot choice and the worst case

Quicksort's cost depends entirely on how balanced the splits are. Each partition looks at every element of its range once. If every pivot lands near the middle, the ranges halve, there are logarithmically many levels, and the total is O(n log n), like merge sort. If every pivot is the smallest or largest element, each partition peels off only the pivot: the ranges shrink by one at a time, there are n levels, and the total is quadratic.

```formula reference
T_good(n) = 2T_good(n / 2) + n
T_bad(n) = T_bad(n − 1) + n
where
T_good(n): the running time on n elements when every pivot is the median, so each split is exactly in half; it grows like n log n
T_bad(n): the running time when every pivot is the smallest or largest element, so each split peels off just one element; it grows like n squared
n: the number of elements in the current sub-array; the "+ n" term is the partition, which looks at every element once
In words: halving every time gives merge sort's n log n; removing only one element each time adds up a shrinking series of partitions, which is quadratic.
```

### Why sorted input is the classic trap

With the first or last element as the pivot, **already sorted input** is the worst case: the last element is the maximum of every range, so each partition compares the pivot with every other element and removes only the pivot. For 100 elements that is 4,950 comparisons and recursion 99 levels deep. For a million elements it is about 500 billion comparisons and, in most languages, a stack overflow long before the end. Reverse-sorted input is just as bad. Sorted and reverse-sorted inputs are common in practice, so this is not theoretical.

Defences:

- **Median-of-three**: use the median of the first, middle and last elements. Fixes sorted and reverse-sorted inputs and gives slightly better splits on random data. Large arrays can use the "ninther" (median of three medians of three).
- **Random pivot**: pick a uniformly random element. Now no particular input is bad; only bad luck is. For every fixed input of **distinct keys**, with fresh independent uniform pivots, the expected number of comparisons is only about **39% more than perfect halving** would need: about 25 million for a million keys, against about 18 million if every pivot were the exact median (the leading term alone, shown below, gives about 28 million). The probability of quadratic behaviour is vanishingly small for large n. Randomising the pivot alone does not rescue Lomuto on all-equal keys, because every split is still empty on one side.

```formula reference
C_avg ≈ 2n ln(n) ≈ 1.39n log_2(n)
where
C_avg: the expected (average) number of comparisons randomised quicksort makes on n distinct keys
n: the number of elements
ln(n): the natural logarithm of n (base e, about 2.718); ln(n) ≈ 0.693 × log_2(n)
log_2(n): the base-2 logarithm of n, how many times n can be halved before reaching 1
≈: approximately equal to (the leading term only; lower-order terms are dropped)
In words: random pivots cost only about 39% more comparisons than perfect halving would, because most pivots land reasonably near the middle.
```

> [!warning] Deterministic pivots can be attacked
> If an attacker knows your pivot rule, they can construct an input that triggers the worst case. McIlroy's 1999 paper "A Killer Adversary for Quicksort" did this against C library `qsort` implementations. For untrusted input, use randomisation or a sort with a worst-case guarantee.

## Key takeaways
- Consistently extreme pivots make a quadratic triangle of comparisons.
- Independent random pivots give an expected guarantee for distinct keys, not an absolute worst-case bound.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
