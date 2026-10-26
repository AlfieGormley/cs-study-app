---
id: cplx-polynomial-time
title: "What polynomial time promises"
level: basic
minutes: 3
summary: "P contains decision problems with deterministic polynomial-time algorithms."
sourceLesson: cplx-p-np
---

## P: the problems we can solve efficiently

**P** (polynomial time) is the set of decision problems solvable by a deterministic algorithm (one with no randomness or guessing) whose worst-case running time is bounded by a polynomial in the input size.

```formula essential
T(n) = O(n^k)   for some k
where
T(n): the worst-case number of steps the algorithm takes on an input of n bits
n: the input size, in bits
k: a constant exponent that does not grow with n, such as 1, 2 or 3
n^k: k copies of n multiplied together (n to the power k)
O(...): Big O: "at most a constant times this, for large n"
In words: a problem is in P when some deterministic algorithm solves every input in at most about n to the power k steps, for one fixed k. Sorting-style O(n^2) and shortest-path-style O(n^3) bounds qualify; 2 to the power n does not.
```

Why draw the line at polynomials?

- **Closure.** A polynomial-time algorithm that calls a polynomial-time subroutine a polynomial number of times is still polynomial. Compose efficient pieces and you stay efficient.
- **Robustness.** Standard classical models, such as Turing machines and bounded-word random-access models with explicit operation costs, simulate each other with polynomial overhead. The broader claim that classical computation efficiently simulates every physically realisable computation is an extended Church–Turing thesis, not a theorem; quantum computation challenges it.
- **Growth matters.** A cubic cost multiplies by a fixed factor when input length doubles. A cost exponential in input length eventually outgrows every fixed polynomial. Faster hardware changes constants, not this distinction.

Problems known to be in P include shortest paths, maximum matching, 2-SAT, linear programming (proven in 1979 with the ellipsoid method) and primality testing (the AKS algorithm, 2002).

> [!warning] Polynomial is not the same as fast
> A polynomial with exponent one hundred is in P but useless. In practice, natural problems in P tend to have small exponents, which is part of why the definition has stuck. Treat membership in P as a growth classification; check the exponent, constants and actual workload before deciding that an algorithm is practical.

## Key takeaways

- P contains decision problems with deterministic polynomial-time algorithms.
- Polynomial time is robust under composition but need not be practical.
- Primality is in P even though trial division is exponential in the bit length.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
