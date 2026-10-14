---
id: sort-merge-theorem-counts
title: Merge recurrence tools and exact counts
level: intermediate
minutes: 3
sourceLesson: sort-merge
summary: The master theorem connects recursive halves to the linear combine step.
---

Here n is the number of input elements. This unit builds on the preceding decision-tree or recurrence proof.

The **master theorem**, a general recipe for divide-and-conquer recurrences, gives the same result:

```formula
T(n) = aT(n / b) + f(n)
a = 2,  b = 2,  f(n) = Θ(n)
T(n) = Θ(n log(n))
where
T(n): the running time on n elements
n: the number of elements
a: the number of recursive calls each call makes; 2 for merge sort
b: the factor each call shrinks the input by; 2, because each half has n / 2 elements
f(n): the work done outside the recursive calls; here the merge, which is linear in n
Θ: Big Theta: exactly this growth rate, up to a constant factor
log: the logarithm (base 2 here; the base only changes a constant)
In words: merge sort is the master theorem's "balanced" case, where the work outside the calls matches the work on every level of the tree.
```

The theorem gives the answer, but the tree shows *why*: every level touches every element exactly once.

Concrete numbers for a million elements:

```formula
n log_2(n) ≈ 10^6 × 20 = 2 × 10^7
n^2 / 4 = 10^12 / 4 = 2.5 × 10^11
where
n: the number of elements, here 1,000,000 (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.9, rounded to 20
n^2: n squared, n × n
10^6: ten to the power 6, a million (similarly 10^7, 10^11, 10^12)
≈: approximately equal to
In words: merge sort needs about 20 million comparisons in the worst case, while insertion sort on shuffled input needs about 250 billion steps, one per inversion.
```

The operation counts differ greatly. **Content gap:** absolute runtimes are omitted because no benchmark environment or implementation was verified.

> [!note] Worst, best and average are all linear times logarithmic growth
> Merge sort always splits in the middle and always merges everything, so its cost hardly depends on the input. Plain merge sort is not adaptive: a sorted input still costs Θ(n log n). Timsort (covered later in this module) fixes that.

The exact worst-case comparison count for top-down merge sort is known, and it is very close to the theoretical minimum (covered later in this module):

```formula
C_w = n⌈log_2(n)⌉ − 2^{⌈log_2(n)⌉} + 1
C_w = 5 × 3 − 2^3 + 1 = 8
where
C_w: the most comparisons top-down merge sort makes on any input of n elements
n: the number of elements; here 5
log_2(n): the base-2 logarithm of n; log_2(5) ≈ 2.32
⌈ ⌉: the ceiling: round up to the next whole number, so ⌈2.32⌉ = 3
2^{⌈log_2(n)⌉}: 2 raised to that rounded-up power: the smallest power of 2 that is at least n (8 for n = 5)
In words: the worst case is roughly n log_2(n) comparisons, minus a correction for n not being a power of 2.
```

For five elements that is 8 comparisons, one more than the minimum of 7 that the relevant unit in this module derives.

## Key takeaways
- The master theorem connects recursive halves to the linear combine step.
- Exact comparison counts refine asymptotic bounds without establishing measured runtimes.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
