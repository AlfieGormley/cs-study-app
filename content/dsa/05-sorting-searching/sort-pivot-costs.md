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

Quicksort's cost depends entirely on how balanced the splits are. Two **recurrences** (costs written in terms of the same cost on smaller inputs) show the two extremes:

```formula
T_good(n) = 2T_good(n / 2) + n
T_good(n) = Θ(n log(n))
T_bad(n) = T_bad(n − 1) + n
T_bad(n) = Θ(n^2)
where
T_good(n): the running time on n elements when every pivot is the median, so each split is exactly in half
T_bad(n): the running time when every pivot is the smallest or largest element, so each split peels off just one element
n: the number of elements in the current sub-array; the "+ n" term is the partition, which looks at every element once
Θ: Big Theta: exactly this growth rate, up to a constant factor
log: the logarithm (base 2 here; the base only changes a constant)
n^2: n squared, n × n
In words: halving every time gives merge sort's n log n; removing only one element each time gives a sum of n + (n − 1) + … + 1, which is quadratic.
```

With the first or last element as the pivot, **already sorted input** is the worst case: each partition peels off one element. Lomuto then compares the pivot with every other element of a sub-array that shrinks by one each time:

```formula
C = (n − 1) + (n − 2) + … + 1
C = (n(n − 1)) / 2
C = 100 × 99 / 2 = 4950
C = 10^6 × (10^6 − 1) / 2 ≈ 5 × 10^11
where
C: the number of comparisons Lomuto quicksort makes on sorted input with a last-element pivot
n: the number of elements; 100 in the first example, 1,000,000 (10^6) in the second
…: "and so on", down to 1
10^6: ten to the power 6, a million; 10^11 is a hundred billion
≈: approximately equal to
In words: sorted input turns quicksort into a triangle of comparisons, about n²/2 of them.
```

For 100 elements the recursion also goes 99 levels deep. For a million elements that is about 500 billion comparisons and a stack overflow. Sorted and reverse-sorted inputs are common in practice, so this is not theoretical.

Defences:

- **Median-of-three**: use the median of the first, middle and last elements. Fixes sorted and reverse-sorted inputs and gives slightly better splits on random data. Large arrays can use the "ninther" (median of three medians of three).
- **Random pivot**: pick a uniformly random element. Now no particular input is bad; only bad luck is. The expected number of comparisons is given below, for every fixed input of **distinct keys**, with fresh independent uniform pivots. Randomizing the pivot alone does not rescue Lomuto on all-equal keys. The probability of quadratic behaviour is vanishingly small for large n.

```formula
C_avg ≈ 2n ln(n)
C_avg ≈ 1.39n log_2(n)
C_avg ≈ 1.39 × 10^6 × 19.93 ≈ 2.8 × 10^7
where
C_avg: the expected (average) number of comparisons randomised quicksort makes on n distinct keys
n: the number of elements; 1,000,000 (10^6) in the last line
ln(n): the natural logarithm of n (base e, about 2.718); ln(n) ≈ 0.693 × log_2(n)
log_2(n): the base-2 logarithm of n, how many times n can be halved before reaching 1; log_2(10^6) ≈ 19.93
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to (the leading term only; lower-order terms are dropped)
In words: with random pivots, quicksort makes only about 39% more comparisons than perfect halving would, around 28 million for a million keys.
```

> [!warning] Deterministic pivots can be attacked
> If an attacker knows your pivot rule, they can construct an input that triggers the worst case. McIlroy's 1999 paper "A Killer Adversary for Quicksort" did this against C library `qsort` implementations. For untrusted input, use randomisation or a sort with a worst-case guarantee.

## Key takeaways
- Consistently extreme pivots make a quadratic triangle of comparisons.
- Independent random pivots give an expected guarantee for distinct keys, not an absolute worst-case bound.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
