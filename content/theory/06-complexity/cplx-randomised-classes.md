---
id: cplx-randomised-classes
title: "Las Vegas, Monte Carlo and decision classes"
level: advanced
minutes: 4
summary: "Las Vegas guarantees correctness; Monte Carlo permits bounded error."
sourceLesson: cplx-randomised-quantum
---

Some of the most useful algorithms flip coins. Miller–Rabin is widely used in probable-prime generation, randomised quicksort illustrates efficient expected-time sorting, and suitable secret keyed hashing can defend against precomputed adversarial collisions; a seed alone does not guarantee resistance to adaptive attacks. Randomness also gives us algorithms for problems where no deterministic polynomial algorithm is known at all.

Quantum computers go further: they manipulate amplitudes that can interfere. This lesson looks at both through complexity classes, and keeps a careful line between what is **proven** and what is **believed**.

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

The same definitions in symbols, where Pr[...] is the probability over the algorithm's own coin flips:

```formula
x ∈ L  gives  Pr[A(x) = 1] ≥ 1/2
x ∉ L  gives  Pr[A(x) = 1] = 0
x ∈ L  gives  Pr[B(x) = 1] ≥ 2/3
x ∉ L  gives  Pr[B(x) = 0] ≥ 2/3
where
L: the decision problem, viewed as the set of its yes-instances
x: any input (problem instance)
∈, ∉: "is a member of", "is not a member of": x ∈ L means x is a yes-instance, x ∉ L a no-instance
A(x), B(x): the algorithm's output on x: 1 means accept (answer yes), 0 means reject (answer no)
A: an RP algorithm: polynomial-time, randomised, with one-sided error (it can miss a yes, but never wrongly says yes)
B: a BPP algorithm: polynomial-time, randomised, with two-sided error (it can be wrong either way, at most 1/3 of the time)
Pr[...]: the probability of the event in brackets, taken over the algorithm's random coin flips, for this fixed input x
≥: is at least
In words: an RP algorithm catches each yes-instance at least half the time and never accepts a no-instance; a BPP algorithm is right at least two-thirds of the time on every input, whichever the answer.
```

coRP swaps the roles (never wrongly rejects a yes-instance; rejects each no-instance with probability at least 1/2). ZPP sits exactly where the one-sided classes overlap:

```formula
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
