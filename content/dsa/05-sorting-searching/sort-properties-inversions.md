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

> [!analogy] Real-world analogy: boarding a plane by group
> An airline calls passengers by boarding group. Within each group, people board in the order they were already standing in line; nobody in group 2 is reshuffled just because they share a group number.
>
> **How it maps:** the boarding group is the sort key, the order in the line is the input order, and keeping that order inside each group is stability. An unstable sort is like staff letting group 2 board in whatever order they happen to pick.
>
> **Where it stops:** staff can see the whole line and simply wave groups forward. A sorting algorithm discovers the order through comparisons and moves, and only some algorithms (insertion sort and merge sort, but not selection sort or heapsort) are built so that equal keys can never pass each other.

### Inversions: a measure of disorder

An **inversion** is a pair of positions `i < j` with `a[i] > a[j]`: an earlier element that is bigger than a later one. A sorted array has 0 inversions.

```
[3, 1, 2]
inversions: (3,1) and (3,2)  ->  2
```

How many inversions can there be? In a reversed array of distinct items, **every pair of positions** is out of order, so a reversed array has the most. `[4, 3, 2, 1]` has 6 inversions, and a reversed array of 1,000 items has 499,500. In a shuffled array each pair is equally likely to be in or out of order, so on average about **half** the pairs are inversions: about 250,000 for 1,000 items. Both counts grow with the square of n.

```formula reference
I_max = (n(n − 1)) / 2
E[I] = (n(n − 1)) / 4
where
I_max: the largest possible number of inversions, reached when n distinct elements are in exactly reverse order
E[I]: the expected (average) number of inversions I when every ordering of the n distinct elements is equally likely
n: the number of elements in the array
In words: a reversed array has every pair of positions out of order, and a shuffled one has about half of those pairs out of order on average; both counts grow with the square of n.
```

Inversions matter because swapping an out-of-order **adjacent** pair removes exactly one inversion; swapping an ordered pair can instead add one. So a sort that only swaps neighbours must do at least as many swaps as there are inversions.

The "half of all pairs" average only holds for a **uniformly random permutation** (every ordering equally likely) of distinct keys. Real data is often far less disordered, which is exactly what adaptive sorts exploit. Still, this single fact explains why bubble and insertion sort are quadratic on average: a quadratic average number of bubble swaps or insertion shifts.

## Key takeaways
- Stability preserves the input order of equal keys.
- Inversions measure pairwise disorder, and adjacent swaps remove one inversion at a time.

## Further reading
- [Elementary sorts — Princeton Algorithms](https://algs4.cs.princeton.edu/21elementary/)
