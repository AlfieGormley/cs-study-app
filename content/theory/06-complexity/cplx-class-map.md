---
id: cplx-class-map
title: "Proven containments and open separations"
level: basic
minutes: 5
summary: "P is contained in NP, PSPACE and EXPTIME; P differs from EXPTIME."
sourceLesson: cplx-p-np
---

## What is proven, and what isn't

The proven facts fit in one chain of classes, plus one separation:

```formula essential
P ⊆ NP ⊆ PSPACE ⊆ EXPTIME
P ≠ EXPTIME
P = NP   gives   NP = coNP
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
coNP: the class coNP: decision problems whose no-answers have a short certificate checkable in polynomial time
PSPACE: decision problems solvable using a polynomial amount of memory (at most about n^k bits), however long it takes
EXPTIME: decision problems solvable in exponential time: at most about 2 to the power n^k steps for some fixed k
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
≠: "is not equal to": here, some problem is in EXPTIME but not in P
n: the input size, in bits
k: a fixed constant exponent
In words: each class in the chain sits inside the next; P is definitely smaller than EXPTIME; and if P were equal to NP, then NP would also equal coNP.
```

Why each piece holds:

- **P is inside NP.** If you can solve the problem, the verifier can ignore the certificate and solve it.
- **NP is inside EXPTIME.** Try every possible polynomial-length certificate.
- **P is not all of EXPTIME.** The *time hierarchy theorem* (Hartmanis and Stearns, 1965) shows that more time solves strictly more problems.
- So in the chain, **at least one** inclusion is strict. Nobody knows which.
- **If P equals NP, NP equals coNP**, because P is closed under complement: flip the answer of a polynomial-time algorithm and it is still polynomial-time.

Enumerating polynomial-length certificates takes exponentially many trials. Running a polynomial-time checker on each still gives an exponential-time algorithm. The distinction is between the time for one check and the number of candidates.

Open problems:

- **P vs NP.** Almost all experts conjecture P differs from NP. It is one of the Clay Millennium Prize problems ($1 million).
- **NP vs coNP.** Conjectured different.
- Whether graph isomorphism or factoring is in P. Neither is known to be NP-complete; Babai (2015, with a fix in 2017) put graph isomorphism in quasi-polynomial time (below).

**Quasi-polynomial time** is a useful upper-bound category between polynomial and ordinary exponential scales. It includes polynomial bounds; proving such an upper bound never proves a problem needs that much time.

```formula reference
t = 2^{O((log n)^c)}
where
t: the running time, in steps
n: the input size, in bits
log: the logarithm (base 2 here; the base only changes the constant)
c: a fixed constant; for c = 1 this is just a polynomial
O(...): Big O: "at most a constant times this, for large n"
2^{...}: 2 raised to that power
In words: exponentiating a fixed power of the logarithm gives a quasi-polynomial bound. These bounds include polynomials and also growth faster than every polynomial but slower than ordinary exponential growth. An upper bound never proves that much time is necessary.
```

The practical lesson is to distinguish an algorithm’s upper bound from a lower bound on every possible algorithm.

```
+-------------- EXPTIME -------------+
| +------------ PSPACE ------------+ |
| | +---- NP -----+                | |
| | |        +----+---- coNP --+   | |
| | |        | P  |            |   | |
| | |        +----+------------+   | |
| | +-------------+                | |
| +--------------------------------+ |
+------------------------------------+
 P sits inside NP ∩ coNP. The picture
 assumes P != NP != coNP; of the
 separations, only P != EXPTIME is
 proven.
```

The NP-to-PSPACE inclusion reuses memory: enumerate every polynomial-size certificate in turn, run the polynomial-time checker, then reuse its workspace for the next. The number of trials affects time, while the storage for one certificate and one checker run stays polynomial.

## Key takeaways

- P is contained in NP, PSPACE and EXPTIME; P differs from EXPTIME.
- Neither P versus NP nor NP versus coNP has been resolved.
- An upper bound such as quasi-polynomial time does not establish a matching lower bound.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
