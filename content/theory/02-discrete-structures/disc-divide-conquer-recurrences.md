---
id: disc-divide-conquer-recurrences
title: "Recursion trees and divide-and-conquer recurrences"
level: intermediate
minutes: 3
summary: "Count work at each recursion-tree level before adding the levels."
sourceLesson: disc-inclusion-recurrences
---

### Divide-and-conquer recurrences

Recursive algorithms that split the input into equal parts give recurrences of a standard shape. Merge sort splits into two halves and merges in linear time. Unrolling its recursion tree shows the same work on every level:

```formula
T(n) = a × T(n / b) + f(n)
T(n) = 2 × T(n / 2) + n
W_i = 2^i × (n / 2^i) = n
L = log_2(n)
T(n) ≈ W_i × L = n × log_2(n)
where
T(n): the running time on an input of size n
n: the positive input size, considered on powers of b for exact equal splits; merge sort here uses powers of 2
a: the fixed positive integer number of recursive calls (subproblems), 2 for merge sort
b: the fixed real factor greater than 1 by which each subproblem is smaller, 2 for merge sort
f(n): the work done outside the recursive calls (splitting and combining), n for merge sort
W_i: the total work on level i of the recursion tree: 2^i subproblems of size n / 2^i each
i: the level, 0 at the top
L: the number of levels before the subproblems reach size 1
log_2: logarithm base 2: how many times you can halve n before reaching 1
≈: approximately (ignoring constant factors and rounding)
In words: merge sort does about n work on each of about log_2(n) levels. For n = 1024 that is 1024 × 10 = 10,240 units of work.
```

The **master theorem** packages this. Compare the outside work f(n) with the work at the leaves of the tree:

```formula
N_leaf = n^{log_b(a)}
n^{log_2(1)} = n^0 = 1
n^{log_2(2)} = n^1 = n
n^{log_2(3)} ≈ n^{1.585}
where
N_leaf: the number of leaves of the recursion tree, which sets the work done at the bottom
n: the positive input size, considered on powers of b for exact equal splits; merge sort here uses powers of 2
a: the fixed positive integer number of recursive calls
b: the fixed real factor greater than 1 by which each call's input shrinks
log_b: logarithm base b: the power you raise b to in order to get its argument
log_2: logarithm base 2; log_2(1) = 0, log_2(2) = 1 and log_2(3) ≈ 1.585
≈: approximately equal to
In words: the last three lines are binary search (a = 1, b = 2), merge sort (a = 2, b = 2) and Karatsuba multiplication (a = 3, b = 2). Roughly, if f(n) grows more slowly than N_leaf, the leaves dominate and the time is about N_leaf; if f(n) matches it, multiply by a factor of log n; if f(n) grows faster, f(n) dominates (each case has technical conditions).
```

So binary search has logarithmic time; merge sort has linear times logarithmic time; and Karatsuba multiplication has the power-law bound shown below.

```formula
T_B(n) = O(log_2(n))
T_M(n) = O(n log_2(n))
T_K(n) = O(n^{log_2(3)})
where
T_B, T_M, T_K: running times of binary search, merge sort and Karatsuba multiplication under their usual arithmetic-cost models
n: the input size
log_2: logarithm to base two
O( ): an upper bound on growth up to a fixed constant factor for sufficiently large input sizes
In words: The first two algorithms respectively have constant and linear work per level. Karatsuba has three half-size subproblems, giving an exponent of about 1.585.
```

A merely slower or faster function is not enough for the usual first and third cases: the gap must be polynomial. For the faster outside-work case, require that the total outside work of the children is eventually at most a fixed fraction, strictly below one, of the parent’s outside work. This regularity condition prevents large oscillations. The equal-order case shown here assumes non-negative outside work matching leaf growth up to constant factors. The DSA subject covers the full theorem in depth.

## Key takeaways

- Count work at each recursion-tree level before adding the levels.
- The master theorem compares outside work with leaf growth under its technical conditions.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
