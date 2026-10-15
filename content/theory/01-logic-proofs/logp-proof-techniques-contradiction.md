---
id: logp-proof-techniques-contradiction
title: Contradiction, irrationality and infinitely many primes
level: intermediate
minutes: 4
sourceLesson: logp-proof-techniques
summary: A contradiction proof assumes the negation of the claim and reaches an impossibility.
---

The earlier parity proof established that an integer whose square is even is itself even. We use that lemma below.

## Proof by contradiction

To prove a statement S: **assume not S (not S) and derive something impossible**, such as a statement and its negation. Since a true assumption cannot lead to a false conclusion, not S must be false, so S is true.

The two classic examples are over 2,000 years old.

### the square root of 2 is irrational

Suppose the square root of 2 is rational. Then it is a fraction a/b of integers with b is not equal to 0, and we may take the fraction in lowest terms (a and b share no factor, as any fraction can be reduced). Square both sides and rearrange:

```formula
√2 = a / b
2 = a^2 / b^2
a^2 = 2b^2
where
√2: the square root of 2, the positive number whose square is 2 (about 1.41421)
a, b: integers with no common factor, b ≠ 0, assumed to satisfy √2 = a / b
a^2, b^2: a and b squared
≠: is not equal to
√: the non-negative square root
In words: if √2 were a fraction a/b, then a² would be exactly twice b², so a² would be even.
```

So a² is even, which means a is even (that is the contrapositive result above). Write a equals 2k and substitute:

```formula
(2k)^2 = 2b^2
4k^2 = 2b^2
b^2 = 2k^2
where
k: the integer with a = 2 × k
b: the denominator from before
In words: b² is twice an integer, so b² is even, and so b is even too.
```

Now a and b are both even, so a/b is not in lowest terms. Contradiction. ∎

The proof uses the earlier contrapositive result as a **lemma**. Building proofs from smaller proven pieces is like building programs from tested functions.

### There are infinitely many primes (Euclid)

Suppose there are only finitely many primes, and list them all as p₁, p₂, …, pₖ. Build a new number N from them:

```formula
N = p_1 × p_2 × ... × p_k + 1
N − p_1 × p_2 × ... × p_k = 1
where
N: the product of every listed prime, plus 1
p_1, p_2, ..., p_k: the supposedly complete list of primes
k: how many primes are on the list
In words: N is one more than the product of all the primes, so subtracting that product from N leaves exactly 1.
```

N is greater than 1, so N has a prime factor q. Since the list is supposed to be complete, q is one of the pᵢ, so q divides the product p₁·p₂·…·pₖ. q also divides N, so q divides their difference, which is 1. No prime divides 1. Contradiction. ∎

> [!warning] A common misreading
> The proof does **not** say N itself is prime. 2 times 3 times 5 times 7 times 11 times 13 plus 1 equals 30031 equals 59 times 509. It says N has a prime factor missing from the list, which is all the contradiction needs.

### Contradiction or contrapositive?

When proving p implies q by contradiction, you assume "p and not q" (written p and not q, where ∧ is AND) and hunt for any impossibility. A contrapositive proof assumes not q and must reach exactly not p. If the derivation of not p uses only not q and background facts, without relying on the additional assumption p, it can be restated as a direct contrapositive proof. Otherwise it remains a contradiction argument.

Contradiction shines when the claim is a negative ("there is no...", "is not rational", "cannot be decided"). In computer science, the proof that the halting problem is undecidable is a proof by contradiction, and contradiction is also useful in many lower-bound arguments.


## Key takeaways
- A contradiction proof assumes the negation of the claim and reaches an impossibility.
- Euclid needs a missing prime factor; the product of listed primes plus one need not itself be prime.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Contraposition — Wikipedia](https://en.wikipedia.org/wiki/Contraposition)
