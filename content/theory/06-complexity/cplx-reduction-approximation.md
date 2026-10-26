---
id: cplx-reduction-approximation
title: "Why exact reductions need not preserve ratios"
level: intermediate
minutes: 3
summary: "Exact decision equivalence does not ensure approximation equivalence."
sourceLesson: cplx-reductions
---

The preceding exact maps connect Independent Set, Vertex Cover and Clique. Approximation additionally asks how a returned feasible solution compares with the optimum. For an objective where lower cost is better, factor two means a cost at most twice optimum; for maximisation it means a value at least half optimum.

Vertex Cover has a polynomial-time factor-two approximation. Complementing the returned cover still produces a valid independent set, but its quality can be arbitrarily poor. If the optimum cover uses half the vertices, a factor-two algorithm may legally return every vertex. Its complement is empty even though a large independent set exists.

For Clique and Independent Set, polynomial-time approximation within a factor equal to any fixed positive power of vertex count below one is NP-hard. This is a worst-case, asymptotic statement under the assumption that P differs from NP.

Exact reductions preserve answers or optimum values in a specified way. Transferring an approximation additionally requires controlling how solution errors change; subtraction from the vertex count can destroy a multiplicative guarantee.

## Key takeaways

- Exact decision equivalence does not ensure approximation equivalence.
- A factor-two cover can leave an empty independent-set complement.
- Clique and independent set have much worse polynomial-time approximation limits.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
