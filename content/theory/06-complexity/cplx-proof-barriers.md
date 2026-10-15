---
id: cplx-proof-barriers
title: "Proof barriers and practical hardness"
level: basic
minutes: 3
summary: "Relativisation, natural proofs and algebrisation limit families of proof techniques."
sourceLesson: cplx-p-np
---

### Why it is so hard to prove

Three known **barriers** rule out whole families of proof techniques:

- **Relativisation** (Baker, Gill and Solovay, 1975): there are oracles (imaginary black-box subroutines) relative to which P equals NP, and others where they differ, so simulation-and-diagonalisation arguments like the halting proof cannot settle it.
- **Natural proofs** (Razborov and Rudich, 1994): a broad class of circuit lower-bound arguments would, if they worked, break pseudorandom functions that are believed secure.
- **Algebrisation** (Aaronson and Wigderson, 2008) extends the relativisation barrier.

## Why practitioners care

- **Recognising the wall.** If your scheduling problem is NP-complete (in the NP-completeness units), stop hunting for a fast exact algorithm for all inputs and reach for approximations, heuristics or solvers (in the coping-strategy units).
- **Cryptography.** Standard computationally secure encryption with short reusable keys requires one-way functions; information-theoretic schemes such as the one-time pad use different key-length assumptions. If one-way functions exist then P and NP are different. The converse is not known: P differs from NP alone would not guarantee secure cryptography, because NP-hardness is about the worst case and crypto needs problems hard on *average*.
- **Worst case is not typical case.** Modern SAT solvers handle many large industrial instances; performance depends strongly on structure and workload. If P and NP differ, NP-hardness rules out a polynomial-time exact algorithm for all inputs; it does not say this particular instance is hard.

## Key takeaways

- Relativisation, natural proofs and algebrisation limit families of proof techniques.
- Worst-case hardness does not establish cryptographic average-case hardness.
- NP-completeness guides algorithm choices without predicting every instance’s difficulty.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
