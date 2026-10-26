---
id: disc-divide-conquer-recurrences
title: "Recursion trees and divide-and-conquer recurrences"
level: intermediate
minutes: 3
summary: "Count work at each recursion-tree level before adding the levels."
sourceLesson: disc-inclusion-recurrences
---

### Divide-and-conquer recurrences

Merge sort splits an input into two halves and combines them with linear work. Each level contains more subproblems, but their total size stays the original input size. For this model assume powers-of-two input sizes, constant positive base cost at size one, and unit-cost operations:

```formula essential
T(n) = 2 × T(n / 2) + n
where
T(n): the running time on an input of size n
n: the positive input size; the recurrence uses powers of two and applies above size one
In words: Merge sort makes two recursive calls on half-sized inputs, then does linear combining work. More calls at deeper levels exactly offset their smaller individual size.
```

The **master theorem** packages this comparison for a fixed number of equal-sized recursive subproblems. Compare work outside the recursive calls with the growth in the number of leaves.

```formula reference
N_leaf = n^{log_b(a)}
where
N_leaf: the number of leaves of the recursion tree, which sets the work done at the bottom
n: the positive input size, a power of the shrink factor b for exact equal splits down to size one
a: the fixed positive integer number of recursive calls
b: the fixed real factor greater than 1 by which each call's input shrinks
log_b: logarithm base b: the power you raise b to in order to get its argument
In words: The number of leaves depends on both how many recursive calls each node creates and how much each call shrinks the input. This reference applies to fixed equal splits down to constant-size leaves.
```

Binary search follows one branch with constant work per level, so it is logarithmic. Merge sort has linear total work per level and logarithmically many levels. Karatsuba multiplication uses three half-size subproblems; its growth lies between linear and quadratic under the usual digit-operation model.

When outside work is polynomially smaller than leaf growth, the leaves dominate. When it matches leaf growth up to constant factors, similar work accumulates across logarithmically many levels. When it is polynomially larger, it dominates only with the usual regularity condition: eventually, the children’s total outside work is at most a fixed fraction below one of the parent’s outside work. Work must be non-negative. A slight growth difference alone does not establish one of these cases; the DSA subject covers the full theorem.

## Key takeaways

- Count work at each recursion-tree level before adding the levels.
- The master theorem compares outside work with leaf growth under its technical conditions.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
