---
id: cplx-identity-primality
title: "Polynomial identities and probable primes"
level: advanced
minutes: 4
summary: "Schwartz–Zippel bounds false zeros using degree and sample-set size."
sourceLesson: cplx-randomised-quantum
---

### Polynomial identity testing

Given an arithmetic circuit over a specified field (a network of additions and multiplications) computing a polynomial in many variables, is that polynomial identically zero, meaning every coefficient cancels? Expanding it can produce exponentially many terms.

The **Schwartz–Zippel lemma** says a random evaluation almost never lands on a root of a nonzero polynomial:

```formula reference
Pr[p(x_1, ..., x_n) = 0] ≤ d / |S|
where
p: the polynomial computed by the circuit, assumed not to be the zero polynomial
x_1, ..., x_n: its n variables, each chosen independently and uniformly at random from S
n: the number of variables
d: an upper bound on the total degree of p, the largest sum of exponents in any term
S: a finite nonempty set of distinct values from the coefficient field
|S|: the number of values in S
Pr[...]: the probability, over the random choice of the variables, of the event in brackets
≤: is at most
In words: for a nonzero polynomial, the false-zero bound is total degree divided by sample-set size. A larger sample set improves the bound; more variables alone do not worsen it.
```

So evaluate at one random point: if the result is nonzero, the polynomial is certainly nonzero. Repeating with independent points multiplies the bounds. Choose each variable independently and uniformly from the same finite set of distinct elements in the coefficient field (or integral domain). A known total-degree upper bound divided by the sample-set size bounds a false zero. The bound is useful when the sample set is larger than that degree bound. Every evaluation of an identically zero polynomial is zero.

For the standard arithmetic-circuit identity-testing problem, with an effective coefficient representation, a computable degree bound and polynomial-cost exact or suitable modular evaluations, polynomial identity testing is in **coRP**, and **no deterministic polynomial-time algorithm is known**. Kabanets and Impagliazzo (2004) showed that derandomising it would imply circuit lower bounds that nobody can currently prove.

### Primality: a derandomisation story

Miller–Rabin declares a composite "probably prime" with probability at most 1/4 per random base, and independent bases multiply:

```formula reference
ε_k ≤ (1/4)^k = 2^{−2 × k}
where
ε_k: the probability that a fixed odd composite passes all k independent rounds
k: the positive number of rounds, each with a fresh uniformly sampled permitted base
(1/4)^k: k copies of one-quarter multiplied together
≤: is at most
≈: approximately equal to
In words: each independent uniformly sampled permitted base reduces a fixed odd composite’s chance of passing all tests by at least another factor of four. A prime is never rejected.
```

This put PRIMES in coRP (composites are detected with one-sided error) decades ago. In 2002 the AKS algorithm put PRIMES in **P**. Practical libraries still use Miller–Rabin because it is efficient; actual performance depends on operand sizes and implementation. The one-quarter bound is for each fixed odd composite with independent uniformly chosen permitted bases, not the posterior probability that a generated candidate is composite after passing.

## Key takeaways

- Schwartz–Zippel bounds false zeros using degree and sample-set size.
- Primality testing illustrates coRP amplification by accepting only when all rounds pass.
- AKS proves primality belongs to deterministic polynomial time.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Randomised complexity — Arora lecture notes](https://users.cs.duke.edu/~reif/courses/complectures/Arora/lec6.pdf)
- [PRIMES is in P — original paper](https://cse.iitk.ac.in/users/manindra/algebra/primality_original.pdf)
