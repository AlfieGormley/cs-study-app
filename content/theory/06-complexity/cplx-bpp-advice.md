---
id: cplx-bpp-advice
title: "Advice strings and derandomisation"
level: advanced
minutes: 3
summary: "A union bound proves one random string works on every input of a fixed length."
sourceLesson: cplx-randomised-quantum
---

BPP has a polynomial-time randomised decision algorithm correct with probability at least two thirds on each input. Independent majority repetition can make its per-input error exponentially small. Advice allows a different helper string for each input length, unlike a single uniform algorithm.

Adleman's argument first amplifies the error below 2 to the power −n for inputs of n bits, then applies a **union bound** (the chance that at least one of several events happens is at most the sum of their chances):

```formula essential
Pr[some x fails] ≤ 2^n ε
Pr[some x fails] < 2^n × 2^{−n} = 1
where
x: one of the possible inputs of length n
n: the input length, in bits
2^n: the number of different inputs of length n
ε: the error probability for each single input after amplification, below 2^{−n}
Pr[some x fails]: the probability that a random coin string gives a wrong answer on at least one input of length n
≤, <: is at most, is less than
In words: if every input fails on less than a 2 to the power −n share of coin strings, then fewer than all coin strings fail on any input, so at least one coin string is right on every input of that length. That string becomes the advice.
```

The advice string has polynomial length because the amplified algorithm uses only polynomially many random bits. The proof gives existence separately for each input length; it supplies no efficient way to find the strings.

Open, and surprising: whether BPP is contained in NP. Nobody has proved that randomised algorithms can be simulated by short certificates.

Conjectured: P equals BPP. Impagliazzo and Wigderson (1997) proved a conditional version:

```formula reference
L ∈ E  and  size(L) = 2^{Ω(n)}
  gives  P = BPP
where
L: some decision problem
E: the class of problems solvable in time 2^{O(n)}, exponential with a linear exponent
∈: "is a member of"
size(L): the smallest number of gates in Boolean circuits deciding L on inputs of n bits
n: the input length, in bits
O(n): Big O: at most a constant times n, for large n
Ω(n): Big Omega: at least a constant times n, for large n
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
In words: if a problem computable in time exponential in input length requires circuits of size exponential in that length, then every bounded-error randomised polynomial-time decision algorithm has a deterministic polynomial-time replacement.
```

The hypothesis is an unproven circuit lower bound, so the result is conditional. Under this hardness assumption, every BPP decision problem has a deterministic polynomial-time algorithm; the proof does not promise the same exponent or a practical implementation. The primality story fits that pattern.

> [!note] What "P equals BPP" would and wouldn't mean
> It wouldn't make randomness useless: randomised algorithms are often simpler or faster by a polynomial factor, and randomness is essential in cryptography, distributed protocols and sampling. It would mean randomness can't turn exponential into polynomial for decision problems.

## Key takeaways

- A union bound proves one random string works on every input of a fixed length.
- The string is non-uniform advice, with no efficient finding algorithm supplied.
- Strong circuit lower bounds would imply P equals BPP.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
