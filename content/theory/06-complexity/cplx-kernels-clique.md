---
id: cplx-kernels-clique
title: "Problem kernels and limits of parameterisation"
level: intermediate
minutes: 3
summary: "High-degree vertices are forced into small vertex covers."
sourceLesson: cplx-coping
---

### Kernelisation

A **problem kernel** is a polynomial-time shrinking step that leaves an equivalent instance whose size depends only on k. Buss's rule for vertex cover, where the degree of a vertex is its number of edges:

1. A vertex with degree greater than k **must** be in any cover of size at most k (otherwise all its more-than-k neighbours would be needed). Take it and decrease k. Repeat this rule until no such vertex remains, rejecting if the budget becomes negative.
2. Afterwards, every vertex has degree at most k, so k vertices cover at most k² edges. If more than k² edges remain, answer no.

Remove isolated vertices as well. What remains is small:

```formula reference
E_max = kk = k^2
V_max = 2k^2
where
E_max: the most edges the remaining instance can have if a cover of size k exists
V_max: the most vertices it can have, since each edge has two ends and no vertex is isolated
k: the remaining cover budget, after forced vertices have been taken
In words: after high-degree vertices are handled, the remaining budget times the maximum degree bounds how many edges any cover can touch. Reject larger instances; removing isolated vertices then bounds the remaining vertex count too. The kernel size depends only on the remaining budget.
```

Kernels are a standard preprocessing step in practical solvers.

### Not everything is FPT

Clique (a set of vertices all joined to each other) parameterised by solution size is **W[1]-hard**: no FPT algorithm is expected unless the parameterised classes FPT and W[1] coincide, and general algorithms still have an input-size exponent growing with the clique size, including speedups using fast matrix multiplication. The **Exponential Time Hypothesis** (ETH; Impagliazzo and Paturi, 2001) conjectures a positive exponential rate for 3-SAT in its number of variables, ruling out subexponential-time algorithms. Under ETH, Clique has no algorithm with a computable parameter-only factor and an input-size exponent growing sublinearly in the requested clique size.

ETH is a conjecture, stronger than P differs from NP.

## Key takeaways

- High-degree vertices are forced into small vertex covers.
- Buss’s rules give a problem kernel bounded in size by the remaining budget.
- Clique is W[1]-hard by solution size; ETH gives stronger conditional exponent limits.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
