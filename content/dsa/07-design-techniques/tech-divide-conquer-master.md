---
id: tech-divide-conquer-master
title: Using the simplified master theorem
level: intermediate
minutes: 4
sourceLesson: tech-divide-conquer
summary: Compare the exponent of local work with the critical leaf-growth exponent.
---

The previous unit defined a recurrence as the work of smaller calls plus the work outside them. Here n is input size, a is the fixed number of calls per split, and b is the fixed shrink factor. We now compare those calls with local work to solve this restricted recurrence family.

### The master theorem (simplified)

The **master theorem** answers that race in one step for recurrences of this shape. It applies when a and b are fixed numbers, the base case costs a constant, and the work outside the recursion is a power of n. This simplified form ignores the rounding of subproblem sizes to whole numbers:

```formula
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

```formula
a = 2, b = 2, d = 1
c = log_2(2) = 1
T(n) = Θ(n log(n))
where
a: the two recursive calls per split
b: the shrink factor, two for halves
d: the exponent of local work, one for linear merging
c: the critical leaf-growth exponent
n: the number of input items
T(n): the unit-cost running time
log_2: the base-two logarithm
log: a logarithm of any fixed base greater than one
Θ: Big-Theta, growth bounded above and below by constant multiples
In words: The local-work and leaf-growth exponents match, so merge sort pays linear work at each logarithmically many levels.
```

More general recurrences (uneven splits, or local work growing linearly times a logarithm) need other tools, such as the full master theorem or the Akra–Bazzi method.

The algorithm names below are an overview; their implementations appear in later units. Each card uses input size n, counting unit-cost arithmetic operations or comparisons as appropriate.

```formula
T(n) = T(n / 2) + O(1)
T(n) = O(log(n))
where
T(n): the algorithm’s running time on input size n
n: the number of searchable items, sorted items, exponent value, digits or points for this named algorithm
log_2: base-two logarithm; log_2(3) is about 1.585
O: Big-O, an asymptotic upper bound
log: logarithm of a fixed base greater than one
In words: Binary search and fast power keep just one half-size subproblem.
```

```formula
T(n) = 2T(n / 2) + O(n)
T(n) = O(n log(n))
where
T(n): the algorithm’s running time on input size n
n: the number of searchable items, sorted items, exponent value, digits or points for this named algorithm
log_2: base-two logarithm; log_2(3) is about 1.585
O: Big-O, an asymptotic upper bound
log: logarithm of a fixed base greater than one
In words: Merge sort and closest pair make two half-size calls with linear combination.
```

```formula
T(n) = 3T(n / 2) + O(n)
T(n) = O(n^{log_2(3)})
where
T(n): the algorithm’s running time on input size n
n: the number of searchable items, sorted items, exponent value, digits or points for this named algorithm
log_2: base-two logarithm; log_2(3) is about 1.585
O: Big-O, an asymptotic upper bound
log: logarithm of a fixed base greater than one
In words: Karatsuba replaces four half-products with three; 1.585 is a rounded presentation of the exact critical exponent, whose derivation follows in its unit.
```

## Key takeaways
- Compare the exponent of local work with the critical leaf-growth exponent.
- The simplified theorem assumes fixed branching and shrink factors and power-shaped local work.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Master theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
