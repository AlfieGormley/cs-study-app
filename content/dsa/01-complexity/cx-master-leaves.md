---
id: cx-master-leaves
sourceLesson: cx-recurrences
title: Master Theorem: leaves dominate
level: advanced
minutes: 4
summary: Find the critical exponent and recognise leaf-dominated recurrences.
---

## The Master Theorem

The Master Theorem solves recurrences of this shape, where every recursive call gets the same fraction of the input:

```formula
T(n) = aT(n / b) + f(n)
a ≥ 1,  b > 1
where
T(n): the running time on an input of size n
a: the number of recursive calls (subproblems) each call makes; a constant of at least 1
b: the factor by which the input shrinks; each subproblem has size n / b; a constant greater than 1
f(n): the work done in one call outside its recursive calls (splitting and combining)
n: the input size
≥: greater than or equal to
In words: a call splits its input into a pieces of size n / b, recurses on each, and does f(n) work of its own.
```

The key quantity is the **critical exponent**. It comes from counting the leaves of the recursion tree:

```formula
depth = log_b(n)
leaves = a^{log_b(n)} = n^{log_b(a)}
c = log_b(a)
where
depth: the number of levels before the input size reaches 1 (n divided by b that many times)
log_b(n): the logarithm of n to base b, the power you raise b to in order to get n
leaves: the number of size-1 calls at the bottom of the tree
a: the number of subproblems per call
b: the shrink factor
n: the input size
c: the critical exponent, log_b(a): the power you raise b to in order to get a
log_b(a): the logarithm of a to base b
In words: the tree branches a ways at each of log_b(n) levels, which makes n^c leaves; n^c is the total cost of the leaf level.
```

The leaf-count term in the card gives the total bottom-level cost; the root costs the outside-work function. Comparing them says which end of the tree wins.

## Case 1

**Case 1: outside work is polynomially smaller than leaf growth.** The leaves dominate:

```formula
f(n) = O(n^{c − ε})  for some ε > 0
T(n) = Θ(n^c)
where
f(n): the work outside the recursive calls
n: the input size
c: the critical exponent, log_b(a)
ε: epsilon, some fixed positive number, however small (0.1 will do if it works)
O: Big-O, at most a constant times
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
In words: if the root's work is smaller than the leaf count by at least a fixed power of n, the leaves dominate and the answer is the number of leaves.
```

## Strassen and Karatsuba

Here is the Strassen recurrence worked through in full:

```formula
T(n) = 7T(n / 2) + Θ(n^2)
c = log_2(7) ≈ 2.807
d = 2 < 2.807
T(n) = Θ(n^{log_2(7)})
T_K(n) = 3T_K(n/2) + n
T_K(n) = Θ(n^{log_2(3)})
log_2(8) = 3
where
T(n): the time to multiply two n-by-n matrices
n: the input size in each example: matrix side length or integer digit count
a = 7: seven half-size matrix multiplications per call
b = 2: each subproblem has half the side length
c: the critical exponent, log_b(a)
log_2(7): the base-2 logarithm of 7, about 2.807
d: the power of n in the outside work (adding matrices of side n costs about n^2)
Θ: Big-Theta, exactly this rate up to constants
≈: approximately equal to
T_K(n): Karatsuba’s operation count on n-digit integers
log_2(3): the base-2 logarithm of three; Karatsuba’s exponent
In words: the outside work grows more slowly than the leaf count, so case 1 applies and the leaves set the cost at about n^2.807.
```

Two examples are famous. **Strassen** uses seven half-size matrix products instead of eight, beating cubic multiplication. **Karatsuba** uses three half-size integer products instead of four, beating quadratic multiplication. The card also gives Karatsuba’s recurrence. Reducing the number of subproblems lowers the critical exponent; with eight matrix products the exponent would be three, matching naive multiplication.

## Key takeaways
- The Master Theorem compares outside work with the recursion tree’s leaf count.
- When outside work is polynomially smaller, the leaves determine the tight bound.
- Reducing the number of subproblems can lower the exponent, as in Strassen and Karatsuba.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Strassen algorithm — Wikipedia](https://en.wikipedia.org/wiki/Strassen_algorithm)
- [Karatsuba algorithm — Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
