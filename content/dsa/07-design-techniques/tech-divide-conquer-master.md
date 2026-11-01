---
id: tech-divide-conquer-master
title: Using the simplified master theorem
level: intermediate
minutes: 4
sourceLesson: tech-divide-conquer
summary: Compare the exponent of local work with the critical leaf-growth exponent.
---

The previous unit wrote a divide-and-conquer cost as the work of a smaller calls on inputs shrunk by a factor b, plus the work f(n) one call does itself. Here n is the input size. This unit compares those two effects to solve a restricted family of recurrences in one step.

Going down the recursion tree, two things happen at once:

- the **number of calls** multiplies by a at every level, so the bottom level ends up with a very large number of leaves;
- the **work per call** shrinks, because each input is b times smaller.

If the per-call work shrinks faster than the calls multiply, the root's own work dominates. If the calls multiply faster, the leaves dominate. If the two balance, every level costs about the same and you pay that once per level.

### The master theorem (simplified)

The **master theorem** settles that race for recurrences of this shape. It applies when a and b are fixed numbers, the base case costs a constant, and the work outside the recursion is a power of n. This simplified form ignores the rounding of subproblem sizes to whole numbers:

```formula essential
f(n) = Θ(n^d)
c = log_b(a)
T(n) = Θ(n^d)            if d > c
T(n) = Θ(n^d log(n))    if d = c
T(n) = Θ(n^c)            if d < c
where
T(n): the running time on an input of size n
n: the input size
f(n): the work one call does outside its recursive calls
d: the exponent of that work; a fixed number of at least 0 (d = 1 means linear work, d = 0 constant work)
n^d: n raised to the power d
a: the number of subproblems per call, at least 1
b: the factor by which each subproblem shrinks, greater than 1
c: the critical exponent: the number of leaves of the recursion tree grows like n^c
log_b(a): the logarithm of a to base b, the power you must raise b to in order to get a; for example log_2(4) = 2
log: logarithm; in Big-O and Big-Theta the base only changes a constant factor
Θ: Big-Theta, "grows at exactly this rate, up to constant factors"
In words: if the root's own work grows faster than the number of leaves, the root wins; if they match, every level costs the same and you pay that once per level, log n times; if the leaves grow faster, the leaves win.
```

| Case | Who dominates |
|---|---|
| combine exponent bigger | the root's combine |
| exponents equal | every level equally |
| leaf exponent bigger | the leaves |

You rarely need to compute anything beyond comparing two small numbers. The algorithms in the following units all fit this shape:

| Algorithm | Calls × size, local work | Result |
|---|---|---|
| Binary search | 1 × half, constant | logarithmic |
| Merge sort | 2 × half, linear | n log n |
| Closest pair | 2 × half, linear | n log n |
| Four-product multiply | 4 × half, linear | quadratic |
| Karatsuba | 3 × half, linear | n to the 1.585 |

Two patterns are worth remembering. Halving the input while keeping one call and constant work (binary search) is the equal case: constant work on each of about log n levels. Keeping linear work but adding more half-size calls pushes the recurrence into the leaves-dominate case, where the number of calls matters more than the combining.

More general recurrences (uneven splits, or local work growing linearly times a logarithm) need other tools, such as the full master theorem or the Akra–Bazzi method.

> [!analogy] Real-world analogy: who does most of the work in a company
> A director splits a job among a few managers and spends some time coordinating; each manager splits their part among their own team and coordinates that; and so on down to front-line staff who just do a small task each.
>
> **How it maps:** each person is a call, the number of direct reports is a, how much smaller each person's share is gives b, and coordination time is the local work f(n). If coordination at the top is heavy and shares shrink quickly, the director's level costs the most (root dominates). If the organisation spreads out so fast that front-line staff vastly outnumber everyone else, their combined effort dominates (leaves dominate). If each layer's total effort is the same, the cost is that amount times the number of layers.
>
> **Where it stops:** real organisations are irregular. The theorem only applies when every call has exactly the same branching factor, the same shrink factor and local work that is a power of the input size.

## Key takeaways
- Compare the exponent of local work with the critical leaf-growth exponent.
- The simplified theorem assumes fixed branching and shrink factors and power-shaped local work.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Master theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
