---
id: cplx-randomised-classes
title: "Las Vegas, Monte Carlo and decision classes"
level: advanced
minutes: 4
summary: "Las Vegas guarantees correctness; Monte Carlo permits bounded error."
sourceLesson: cplx-randomised-quantum
---

Some of the most useful algorithms flip coins. Miller–Rabin is widely used in probable-prime generation, randomised quicksort illustrates efficient expected-time sorting, and suitable secret keyed hashing can defend against precomputed adversarial collisions; a seed alone does not guarantee resistance to adaptive attacks. Randomness also gives us algorithms for problems where no deterministic polynomial algorithm is known at all.

Quantum computers go further: they manipulate amplitudes that can interfere. The later quantum lessons compare those capabilities with the randomised classes introduced here.

## Two kinds of randomised algorithm

- **Las Vegas**: always correct, running time is random. Randomised quicksort with distinct keys and uniform random pivots: always sorts, in an expected O(n log n) comparisons, where n is the number of keys.
- **Monte Carlo**: a bounded running-time guarantee, but some chance of a wrong answer. Actual running time can still vary. Miller–Rabin: may call a composite "probably prime".

The error probability is over the algorithm's own coin flips, for **every** input. No assumption about the input being random is needed.

## The classes

RP, coRP and BPP use a worst-case polynomial time bound; ZPP uses expected polynomial time.

| Class | If answer is yes | If answer is no |
|---|---|---|
| RP | accept with probability at least one half | always reject |
| coRP | always accept | reject with probability at least one half |
| BPP | accept with probability at least two thirds | reject with probability at least two thirds |
| ZPP | never wrong | expected poly time |

For RP, acceptance is conclusive; rejection may be a missed yes-instance. For coRP, rejection is conclusive; acceptance may be a missed no-instance. BPP has neither conclusive answer on a single run.

coRP swaps the roles (never wrongly rejects a yes-instance; rejects each no-instance with probability at least 1/2). ZPP sits exactly where the one-sided classes overlap:

```formula essential
ZPP = RP ∩ coRP
where
ZPP: zero-error probabilistic polynomial time: decision problems a randomised algorithm always answers correctly, in expected polynomial time
RP: randomised polynomial time: polynomial-time randomised algorithms that never accept a no-instance and accept each yes-instance with probability at least 1/2
coRP: the complements of RP problems: never reject a yes-instance, and reject each no-instance with probability at least 1/2
∩: intersection: the problems that belong to both classes
In words: a problem has a zero-error, expected-polynomial-time algorithm exactly when it has both kinds of one-sided-error algorithm. Run both repeatedly until one of them gives an answer that is certain.
```

The constants 1/2 and 2/3 don't matter, thanks to amplification.

## Key takeaways

- Las Vegas guarantees correctness; Monte Carlo permits bounded error.
- RP and coRP put errors on opposite input types.
- Combining both one-sided algorithms yields zero-error expected polynomial time.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
