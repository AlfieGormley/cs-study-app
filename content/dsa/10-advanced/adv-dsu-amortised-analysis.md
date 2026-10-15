---
id: adv-dsu-amortised-analysis
title: Understanding inverse-Ackermann bounds
level: intermediate
minutes: 4
summary: Initialisation and later operations have separate costs.
sourceLesson: adv-union-find
---

## How fast is it?

In this table n is the number of elements and m counts the complete sequence of finds and unions, including the unions that create any long path. Initialisation is charged separately. O(f) means "grows at most in proportion to f".

| Version | Cost per operation |
|---|---|
| Naive | O(n) worst case |
| Union by size or rank | O(log n) worst case |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

**α(n)** is the inverse Ackermann function. The Ackermann function A grows so absurdly fast that its inverse barely moves. Under one common convention it is defined like this:

```formula
α(n) = min k such that A(k, k) ≥ n
A(1, 1) = 3
A(2, 2) = 7
A(3, 3) = 61
α(61) = 3
α(n) ≤ 4   for all n ≤ A(4, 4)
α(10^9) = 4
where
α(n): alpha of n, the inverse Ackermann function: the smallest whole number k for which A(k, k) reaches n
A(k, k): the two-argument Ackermann–Péter function with both arguments equal to k; each step up in k makes it explode
A(4, 4): 2 raised to the power (2 raised to the power (2 raised to the power 65536)), minus 3: vastly greater than 10^80, used here only as a numerical scale for comparison
k: a whole number 0, 1, 2, …
n: the number of elements in the union-find structure
min: the smallest value that satisfies the condition
≥: is at least
≤: is at most
In words: α(n) is the number of times you must step up the Ackermann ladder before it passes n, and for every n you could ever store that is at most 4.
```

The last line is the worked example: a billion elements is more than the diagonal’s sixty-one at argument three, but far below its value at argument four, so alpha of a billion is 4. Other textbooks use slightly different conventions and get 3 or 5 instead, but always a tiny constant. In practice, treat each operation as constant time; just say "amortised inverse Ackermann" when asked.

This bound, proved by Robert Tarjan in 1975, is also tight: Fredman and Saks showed in 1989 that a matching inverse-Ackermann lower bound holds in the cell-probe model with logarithmic-size words for suitable operation sequences.

"Amortised" matters. An individual `find` can still walk a long path once, but it flattens that path as it goes. Averaged over a whole sequence, the total is bounded:

```formula
T(m) = O(m α(n))
T_init = O(n)
where
T(m): the total time for m find and union operations after the structure is set up
T_init: the one-off time to create n singleton sets (one element each)
m: the number of operations
n: the number of elements
α(n): the inverse Ackermann function of n, at most 4 in practice
O(f): "grows at most in proportion to f", ignoring constant factors
In words: m operations together cost about m times a tiny constant, plus a one-off cost proportional to n to set things up.
```

For example, 10 million operations on a million elements give an illustrative scaling factor of about forty million, plus linear initialisation. This is a substitution into an asymptotic model, not a measured or guaranteed count of primitive operations. One unlucky `find` inside that run may be slow; the bound is only on the total.

> [!note] Rank after compression
> Path compression changes heights but never updates ranks. That is fine: rank was only ever an *upper bound* on height, but the inverse-Ackermann proof also uses rank-growth and node-count invariants, not just this upper bound.

## Key takeaways

- Initialisation and later operations have separate costs.
- Inverse-Ackermann bounds apply to a sequence, not a fixed operation-step count.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
- [Tarjan’s original Union-Find analysis](https://deltadbu.github.io/UCAS_algorithm_course/Lectures/Union-Find-Tarjan1975.pdf)
