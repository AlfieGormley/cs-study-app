---
id: cplx-conp-certificates
title: "Certificates for no-answers"
level: basic
minutes: 3
summary: "coNP is the complement class of NP, with short certificates for no-instances."
sourceLesson: cplx-p-np
---

## coNP: short proofs of "no"

**coNP** contains the complements of NP problems: decision problems where every *no*-instance has a polynomial-size certificate that a deterministic polynomial-time verifier can check. UNSAT ("this formula has no satisfying assignment") and TAUTOLOGY are the standard examples.

The asymmetry is real. To convince you a formula is satisfiable, I hand you an assignment. To convince you it is *unsatisfiable*, nobody knows a short certificate in general; SAT solvers emit resolution proofs, but for some formulas (like the pigeonhole principle) every resolution proof is exponentially long.

Some problems are in both NP and coNP: both yes-answers and no-answers have short, quickly checkable certificates.

"Does N have a prime factor below k?" is one. For positive integers at least two, a yes-certificate is such a prime factor; a no-certificate is the full prime factorisation (each prime can itself be checked in polynomial time, by AKS). Problems in both NP and coNP are widely believed not to be NP-complete, since that would force NP and coNP to be equal.

## Key takeaways

- coNP is the complement class of NP, with short certificates for no-instances.
- General unsatisfiability is not known to have polynomial-size checkable certificates.
- Bounded-factor decision has certificates for both answers through prime factorisation.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
