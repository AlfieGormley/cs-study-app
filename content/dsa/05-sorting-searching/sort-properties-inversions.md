---
id: sort-properties-inversions
title: Sorting properties and inversions
level: basic
minutes: 5
sourceLesson: sort-simple
summary: Stability preserves the input order of equal keys.
---

Bubble sort is rarely the right general-purpose library sort. So why learn the three "simple" sorts?

Because they are small enough to hold in your head, and each one makes a different trade-off visible. Selection sort minimises writes. Insertion sort exploits order that is already there. Bubble sort shows why "obviously correct" can still be slow. And the vocabulary they introduce (stable, in-place, adaptive) is exactly the vocabulary you need to choose between production sorts later.

Insertion sort is not just a teaching tool either: it runs inside Timsort, introsort and pdqsort for small sub-arrays.

## The vocabulary

Before the algorithms, a note on notation. Throughout this lesson, **n** is the number of elements being sorted. Costs are written in **Big O** notation, which describes how a cost grows as n grows and ignores constant factors:

- O(1): a fixed amount, however large n is.
- O(n): grows in proportion to n. Twice the elements, about twice the cost.
- O(n²): grows with the square of the input size. Twice the elements, about four times the cost.
- O(log n): grows with the logarithm of n, the number of times you can halve n before reaching 1. It is about 20 for a million elements.

O(...) is an upper bound ("at most this fast-growing"). **Θ** (Big Theta) means "exactly this growth rate, up to a constant factor", and **Ω** (Big Omega) means "at least this growth rate".

Now the four properties that every sort in this module will be judged on.

- **In-place**: uses O(1) extra memory beyond the input (some definitions allow O(log n) for a recursion stack). Bubble, selection and insertion are all in-place.
- **Stable sort**: equal keys keep their original relative order. If you sort orders by date and two orders share a date, a stable sort leaves them in the order they arrived.
- **Adaptive**: runs faster when the input is already partly sorted.
- **Online algorithm**: can sort a stream, accepting elements one at a time.

We also count two different costs: **key comparisons** (is `a[i] < a[j]`?) and **moves** (swaps or writes). They matter in different settings. Comparing two long strings is expensive; writing to flash memory wears it out.

### Inversions: a measure of disorder

An **inversion** is a pair of positions `i < j` with `a[i] > a[j]`: an earlier element that is bigger than a later one. A sorted array has 0 inversions.

```
[3, 1, 2]
inversions: (3,1) and (3,2)  ->  2
```

How many inversions can there be? An array of n elements has a fixed number of pairs of positions, and in a reversed array of distinct items every one of those pairs is out of order. That gives the maximum:

```formula
I_max = (n(n − 1)) / 2
I_max = 4 × 3 / 2 = 6
where
I_max: the largest possible number of inversions, reached when the array is in exactly reverse order
n: the number of elements in the array (all distinct); here 4, as in [4, 3, 2, 1]
In words: each of the n elements can pair with the n − 1 others, and dividing by 2 stops each pair being counted twice; in a reversed array every pair is an inversion.
```

So `[4, 3, 2, 1]` has 6 inversions, and a reversed array of 1,000 items has 499,500.

Inversions matter because swapping an out-of-order **adjacent** pair removes exactly one inversion; swapping an ordered pair can instead add one. So a sort that only swaps neighbours must do at least as many swaps as there are inversions. On a typical shuffled input, that is about half the maximum:

```formula
E[I] = (n(n − 1)) / 4
E[I] = 1000 × 999 / 4 = 249750
where
E[I]: the expected (average) number of inversions I, averaged over every possible ordering of the input
n: the number of elements, all distinct and in a uniformly random order; here 1,000
In words: each pair is out of order with probability one half, so on average half of the n × (n − 1) / 2 pairs are inversions.
```

This only holds for a **uniformly random permutation** (every ordering equally likely) of distinct keys. Real data is often far less disordered, which is exactly what adaptive sorts exploit. Still, this single fact explains why bubble and insertion sort are quadratic on average: a quadratic average number of bubble swaps or insertion shifts.

## Key takeaways
- Stability preserves the input order of equal keys.
- Inversions measure pairwise disorder, and adjacent swaps remove one inversion at a time.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
