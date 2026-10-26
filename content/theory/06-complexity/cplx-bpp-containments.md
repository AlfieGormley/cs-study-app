---
id: cplx-bpp-containments
title: "What is proven about BPP"
level: advanced
minutes: 3
summary: "RP is in NP because an accepting random string is a certificate."
sourceLesson: cplx-randomised-quantum
---

## How BPP relates to the rest

The proven containments:

```formula essential
P ⊆ ZPP ⊆ RP ⊆ BPP
RP ⊆ NP
BPP ⊆ PSPACE
BPP ⊆ Σ₂ ∩ Π₂
BPP ⊆ P/poly
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
ZPP: zero-error probabilistic polynomial time: always correct, expected polynomial time
RP: randomised polynomial time with one-sided error: never accepts a no-instance, accepts each yes-instance with probability at least 1/2
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
PSPACE: decision problems solvable with a polynomial amount of memory, however long it takes
Σ₂: the second level of the polynomial hierarchy: problems of the form "there exists y such that for all z, a polynomial-time check R(x, y, z) holds", with y and z of polynomial length
Π₂: the mirror image of Σ₂: "for all y there exists z" (the complements of Σ₂ problems)
∩: intersection: the problems in both classes
P/poly: problems solvable by polynomial-size circuits, one circuit per input length (equivalently, polynomial time with a polynomial-length advice string that depends only on the input length)
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
In words: zero-error and one-sided classes sit inside bounded two-sided randomness. RP specifically sits inside NP because its accepting runs cannot be false positives. BPP fits inside polynomial space, the second level of the polynomial hierarchy and polynomial-size circuits.
```

Why each holds:

- **The chain and RP inside NP.** A zero-error algorithm can be cut off and made one-sided; one-sided error is a special case of two-sided. For RP, an accepting coin sequence is a certificate, since no coin sequence makes it accept a no-instance.
- **BPP inside PSPACE.** Try every coin sequence one after another, count acceptances and reuse the space.
- **BPP inside Σ₂ ∩ Π₂** (Sipser, Gács and Lautemann, 1983). So if P equals NP, the whole polynomial hierarchy collapses to P and P equals BPP.
- **BPP inside P/poly**, explained in the advice-string unit. Adleman (1978) proved it for one-sided error (RP); Bennett and Gill (1981) extended it to BPP, and the result is often called Adleman's theorem. The coin string it finds is non-uniform advice, not a known efficient way to find it.

## Key takeaways

- RP is in NP because an accepting random string is a certificate.
- BPP is in PSPACE and in the second level of the polynomial hierarchy.
- BPP being contained in NP is still open.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
