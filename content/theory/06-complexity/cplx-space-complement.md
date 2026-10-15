---
id: cplx-space-complement
title: "Why NL equals coNL"
level: advanced
minutes: 3
summary: "Immerman–Szelepcsényi closes nondeterministic space under complement."
sourceLesson: cplx-space
---

NL is nondeterministic logarithmic working space, with input kept separately read-only. Directed reachability is NL-complete. Here the complement asks for a certificate that the destination is unreachable; this is distinct from finding a path.

## NL equals coNL

**Immerman–Szelepcsényi theorem (proved independently, 1987–88)**:

```formula
NSPACE(s) = coNSPACE(s)   for s ≥ log n
NL = coNL
where
NSPACE(s): problems a nondeterministic machine decides using at most a constant times s work cells
coNSPACE(s): the complements of those problems (yes and no swapped)
NL: nondeterministic logarithmic space
coNL: the complements of NL problems
s: a space-constructible space bound, in cells
n: the input size, in bits
log: logarithm base 2
≥: is at least
In words: for nondeterministic space of at least log n, a class equals its complement class. In particular **NL equals coNL**: a nondeterministic log-space machine can certify that t is *unreachable* from s.
```

The proof is "inductive counting": nondeterministically compute the exact number of vertices reachable within 1 step, then within 2 steps, and so on up to n steps, using each count to verify the next. Knowing exactly how many vertices are reachable lets the machine confirm t isn't among them.

The analogous question for time, NP vs coNP, is open and believed to go the other way.

At linear rather than logarithmic space, the same complement theorem applies to context-sensitive languages, recognised by linear-bounded nondeterministic machines. For 2-SAT unsatisfiability, guess a variable and directed implication paths both from it to its negation and back; this uses nondeterministic logarithmic space. Complement closure then puts 2-SAT satisfiability in NL too.

## Key takeaways

- Immerman–Szelepcsényi closes nondeterministic space under complement.
- Inductive counting certifies directed unreachability in NL.
- The result covers linear space too and says nothing comparable about NP versus coNP.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
