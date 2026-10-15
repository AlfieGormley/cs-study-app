---
id: cplx-completeness-recipe
title: "Proving a new problem complete"
level: intermediate
minutes: 3
summary: "Show NP membership and reduce a known NP-complete problem to the new problem."
sourceLesson: cplx-np-completeness
---

## Karp's 21 and the domino effect

In 1972 Richard Karp showed 21 well-known problems NP-complete by chaining reductions from SAT: clique, vertex cover, set cover, Hamiltonian cycle, graph colouring, knapsack, and more. Garey and Johnson's 1979 book catalogued hundreds. Today there are thousands.

The recipe for showing a new problem X is NP-complete:

1. Show **X is in NP** (give the certificate and verifier).
2. Pick a known NP-complete problem Y.
3. Give a polynomial-time translation f **from Y to X**: transform instances of the *known* hard problem into instances of X.
4. Prove **both** directions: a yes-instance of Y maps to a yes-instance of X, and a yes-instance produced by f comes only from a yes-instance of Y.

```formula
X ∈ NP
Y ≤_p X   with Y ∈ NPC
y ∈ Y  gives  f(y) ∈ X
f(y) ∈ X  gives  y ∈ Y
where
X: the new problem you want to classify
Y: a known NP-complete problem, such as 3-SAT
y: any instance of Y
f: the polynomial-time translation from instances of Y to instances of X
f(y): the instance of X built from y
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
NPC: the set of NP-complete problems
≤_p: "polynomial-time reduces to": Y ≤_p X means f maps every instance of Y to an instance of X with the same yes/no answer
∈: "is a member of"; y ∈ Y means y is a yes-instance of Y
In words: show X is in NP, then translate a known NP-complete problem into X and prove the translation keeps yes as yes and no as no.
```

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
