---
id: cplx-completeness-recipe
title: "Proving a new problem complete"
level: intermediate
minutes: 3
summary: "Show NP membership and reduce a known NP-complete problem to the new problem."
sourceLesson: cplx-np-completeness
---

## Karp's 21 and the domino effect

In 1972 Richard Karp showed 21 well-known problems NP-complete by chaining reductions from SAT: clique, vertex cover, set cover, Hamiltonian cycle, graph colouring, knapsack, and more. Garey and Johnson's 1979 book catalogued hundreds. This lets each new proof reuse earlier work.

The recipe for showing a new problem X is NP-complete:

1. Show **X is in NP** (give the certificate and verifier).
2. Pick a known NP-complete problem Y.
3. Give a polynomial-time translation f **from Y to X**: transform instances of the *known* hard problem into instances of X.
4. Prove **both** directions: a yes-instance of Y maps to a yes-instance of X, and a yes-instance produced by f comes only from a yes-instance of Y.

The commonest mistake is reducing in the wrong direction. Reducing X to SAT only proves X is no harder than SAT, which is true of every problem in NP.

## Where you meet it in practice

- **Package managers.** Deciding whether a set of packages with versioned dependencies and conflicts can be installed together is NP-complete. libsolv (behind openSUSE's zypper and Fedora's dnf) solves it with a SAT solver.
- **Register allocation** is graph colouring in disguise (Chaitin, 1981); compilers use heuristics.
- **Puzzles**: generalised Sudoku and Minesweeper consistency are NP-complete.

## Key takeaways

- Show NP membership and reduce a known NP-complete problem to the new problem.
- Prove both directions and a polynomial construction bound.
- Dependency resolution, register allocation and generalised puzzles illustrate the method.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
