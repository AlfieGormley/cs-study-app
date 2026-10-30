---
id: sort-comparison-average-bound
title: Stirling estimates and average comparisons
level: intermediate
minutes: 2
sourceLesson: sort-heapsort-lower-bound
summary: Stirling’s formula estimates factorial growth and the comparison lower bound.
---

Here n is the number of input elements. This unit builds on the decision-tree counting argument in the previous unit.

**Stirling's approximation**, a standard estimate of n factorial, makes the bound sharper: the minimum worst-case number of comparisons is about n log₂ n minus roughly 1.44 per element. For a million elements that is about 18.5 million comparisons, compared with the rough n log₂ n figure of about 20 million.

```formula reference
log_2(n!) ≈ n log_2(n) − 1.44n
where
log_2(n!): the base-2 logarithm of n factorial: an information lower bound on worst-case comparisons to sort n distinct elements; round upward for a whole number of comparisons
n: the number of elements
log_2(n): the base-2 logarithm of n
1.44: log_2(e), where e ≈ 2.718 is the base of natural logarithms; it comes from Stirling's formula
≈: approximately equal to (lower-order terms dropped)
In words: the information lower bound is n log_2(n) minus about 1.44 comparisons per element.
```

So **every comparison sort needs Ω(n log n) comparisons in the worst case**. Merge sort and heapsort are **asymptotically optimal**: no comparison sort beats them by more than a constant factor.

The same argument works for the **average** case. A binary tree with many leaves cannot have all of them shallow: if a tree has N leaves, their average depth is at least log₂ N. A comparison sort's tree has one reachable leaf for each of the n factorial orderings of distinct keys, so averaged over all orderings it still needs about log₂(n!) comparisons, which is again Ω(n log n).

That average is taken over every distinct-key permutation being equally likely, and it also bounds the expected comparisons of correct randomised sorts. It is not a bound for every input distribution: an adaptive sort can still be linear on already sorted data, because that is only one of the many orderings being averaged.

## Key takeaways
- Stirling’s formula estimates factorial growth and the comparison lower bound.
- The uniform-permutation average also requires logarithmic decision-tree depth.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
