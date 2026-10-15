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

```formula
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
- **NP is inside EXPTIME.** Try every possible certificate (counted below).
- **P is not all of EXPTIME.** The *time hierarchy theorem* (Hartmanis and Stearns, 1965) shows that more time solves strictly more problems.
- So in the chain, **at least one** inclusion is strict. Nobody knows which.
- **If P equals NP, NP equals coNP**, because P is closed under complement: flip the answer of a polynomial-time algorithm and it is still polynomial-time.

The brute-force argument for NP inside EXPTIME counts certificates:

```formula
N_cert < 2^{p(n) + 1}
t ≤ 2^{p(n) + 1}q(n)
where
N_cert: the number of possible binary certificates of length at most p(n) bits (the geometric sum is smaller than the displayed upper bound)
p(n): the polynomial limit on certificate length, in bits, for an input of n bits
n: the input size, in bits
t: the total running time of the brute-force search, in steps
q(n): the polynomial running time of the verifier on one certificate
2^{p(n)}: 2 to the power p(n): each of the p(n) bits can be 0 or 1
≤: is at most
In words: try every possible certificate and run the checker on each. That is exponentially many polynomial-time checks, which is still exponential time.
```

Open problems:

- **P vs NP.** Almost all experts conjecture P differs from NP. It is one of the Clay Millennium Prize problems ($1 million).
- **NP vs coNP.** Conjectured different.
- Whether graph isomorphism or factoring is in P. Neither is known to be NP-complete; Babai (2015, with a fix in 2017) put graph isomorphism in quasi-polynomial time (below).

**Quasi-polynomial time** sits between polynomial and exponential:

```formula
t = 2^{O((log n)^c)}
where
t: the running time, in steps
n: the input size, in bits
log: the logarithm (base 2 here; the base only changes the constant)
c: a fixed constant; for c = 1 this is just a polynomial
O(...): Big O: "at most a constant times this, for large n"
2^{...}: 2 raised to that power
In words: two to the power of a polylogarithm. The representative function with exponent (log n)^c grows faster than every polynomial when c is greater than one, but far slower than two to the power n. An O upper bound alone does not prove an algorithm needs super-polynomial time.
```

At an input size of a million, the square of its base-two logarithm is about 400, so 2 to that power is huge but nothing like 2 to the power one million.

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
