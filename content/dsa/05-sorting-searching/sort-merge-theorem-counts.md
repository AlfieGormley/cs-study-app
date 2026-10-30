---
id: sort-merge-theorem-counts
title: Merge recurrence tools and exact counts
level: intermediate
minutes: 3
sourceLesson: sort-merge
summary: The master theorem connects recursive halves to the linear combine step.
---

Here n is the number of input elements. This unit builds on the recursion-tree view of merge sort in the previous unit.

The **master theorem** is a general recipe for divide-and-conquer recurrences. It reaches the same answer as the recursion tree by comparing two things: how fast the subproblems shrink, and how much work each call does outside its recursive calls. Merge sort makes two half-size calls and does linear work to merge, which is the theorem's "balanced" case: every level of the tree costs the same, so the total is that per-level cost times the number of levels.

```formula reference
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
In words: with two half-size calls and a linear merge, the work outside the calls matches the work on every level of the tree, so merge sort grows like n log n.
```

The theorem gives the answer, but the tree shows *why*: every level touches every element exactly once. The same reasoning predicts what happens if the combine step changes. A combine step that costs more than linear time adds that extra cost on every level; one that costs only constant time leaves the total linear.

For a million elements the gap is dramatic: merge sort needs about 19 million comparisons in the worst case, while insertion sort on shuffled input needs about 250 billion shifts, one per inversion. Those are operation counts, not timings; how long each takes depends on the implementation and hardware.

> [!note] Worst, best and average are all linear times logarithmic growth
> Merge sort always splits in the middle and always merges everything, so its cost hardly depends on the input. Plain merge sort is not adaptive: a sorted input still costs Θ(n log n). Timsort (covered later in this module) fixes that.

The exact worst-case comparison count for top-down merge sort is known, and it is very close to the theoretical minimum covered later in this module. For five elements it is 8 comparisons, one more than the minimum of 7.

```formula reference
C_w = n⌈log_2(n)⌉ − 2^{⌈log_2(n)⌉} + 1
where
C_w: the most comparisons top-down merge sort makes on any input of n elements
n: the number of elements
log_2(n): the base-2 logarithm of n
⌈ ⌉: the ceiling: round up to the next whole number
2^{⌈log_2(n)⌉}: 2 raised to that rounded-up power: the smallest power of 2 that is at least n
In words: the worst case is roughly the input size times its rounded-up base-2 logarithm, minus a correction for sizes that are not a power of 2.
```

## Key takeaways
- The master theorem connects recursive halves to the linear combine step.
- Exact comparison counts refine asymptotic bounds without establishing measured runtimes.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
