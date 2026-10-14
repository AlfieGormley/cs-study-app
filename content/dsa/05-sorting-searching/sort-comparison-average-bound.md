---
id: sort-comparison-average-bound
title: Stirling estimates and average comparisons
level: intermediate
minutes: 2
sourceLesson: sort-heapsort-lower-bound
summary: Stirling’s formula estimates factorial growth and the comparison lower bound.
---

Here n is the number of input elements. This unit builds on the preceding decision-tree or recurrence proof.

**Stirling's approximation**, a standard estimate of n!, is sharper:

```formula
log_2(n!) ≈ n log_2(n) − 1.44n
log_2(10^6 !) ≈ 1.993 × 10^7 − 1.44 × 10^6
log_2(10^6 !) ≈ 1.85 × 10^7
where
log_2(n!): the base-2 logarithm of n factorial: an information lower bound on worst-case comparisons to sort n distinct elements; round upward for an integer comparison count
n: the number of elements; here a million (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.93
1.44: log_2(e), where e ≈ 2.718 is the base of natural logarithms; it comes from Stirling's formula
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to (lower-order terms dropped)
In words: the information lower bound is n log_2 n minus about 1.44 comparisons per element: about 18.5 million for a million elements.
```

So **every comparison sort needs Ω(n log n) comparisons in the worst case**. Merge sort and heapsort are **asymptotically optimal**: no comparison sort beats them by more than a constant factor.

The same argument works for the **average** case. A binary tree with many leaves cannot have all of them shallow:

```formula
d_avg ≥ log_2(N)
N = n!  ⇒  d_avg ≥ log_2(n!)
where
d_avg: the average depth of a leaf, with every leaf weighted equally: the average number of comparisons
N: reachable leaves of the Boolean comparison tree after pruning impossible branches, one for each distinct-key permutation
n!: n factorial, the number of orderings of n distinct elements
n: the number of elements
log_2: the base-2 logarithm
⇒: "which means"
≥: greater than or equal to
In words: a binary tree with N leaves has average leaf depth at least log_2(N), so averaged over all n! orderings a comparison sort still needs about log_2(n!) comparisons.
```

Averaging over all distinct-key permutations gives Ω(n log n), including expected comparisons of correct randomized sorts. This is not a bound for every nonuniform input distribution.

## Key takeaways
- Stirling’s formula estimates factorial growth and the comparison lower bound.
- The uniform-permutation average also requires logarithmic decision-tree depth.

## Further reading
- [Priority queues and heapsort — Princeton Algorithms](https://algs4.cs.princeton.edu/24pq/)
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
