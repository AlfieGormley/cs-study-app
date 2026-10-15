---
id: disc-modular-inverses
title: "Modular inverses and finite fields"
level: advanced
minutes: 3
summary: "An inverse exists exactly when the integer and modulus have greatest common divisor one."
sourceLesson: disc-number-theory
---

## Modular inverses

The **modular inverse** of a modulo n is the number that multiplies a to give 1, in remainder arithmetic. It plays the role that 1/a plays for ordinary fractions:

```formula
a × a^{−1} ≡ 1 (mod n)
a × x + n × y = 1
a × x ≡ 1 (mod n)
where
a: the integer you want to "divide by"
n: the modulus, an integer at least 2 for these nonzero inverse representatives
a^{−1}: the inverse of a modulo n, a number from 1 to n − 1 (not the fraction 1/a)
x, y: Bézout coefficients from the extended Euclidean algorithm
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: an inverse exists exactly when a and n share no common factor greater than 1 (their gcd is 1, called coprime). Then Bézout gives a × x + n × y = 1, and since n × y is a multiple of n, a × x leaves remainder 1, so x is the inverse.
```

Worked example: the inverse of 7 modulo 40.

```formula
7 × (−17) + 40 × 3 = 1
7^{−1} ≡ −17 ≡ −17 + 40 = 23 (mod 40)
7 × 23 = 161 = 4 × 40 + 1
where
7^{−1}: the inverse of 7 modulo 40
≡: is congruent to: leaves the same remainder after dividing by 40
mod: "modulo": remainders after dividing by 40
In words: the extended algorithm gives −17 as the coefficient of 7; adding 40 makes it positive, 23, and 7 × 23 = 161 really does leave remainder 1 when divided by 40.
```

If the gcd is bigger than 1 there is no inverse: 6 has none modulo 10, because every multiple of 6 is even and so leaves an even remainder, never 1. Python 3.8+ does this for you: `pow(7, -1, 40)` returns `23`, and raises `ValueError` if no inverse exists.

When the modulus is a prime, every nonzero residue has an inverse. That makes the residues modulo a prime a field: addition, subtraction and multiplication are defined, and division by nonzero residues is possible. Elliptic curves and Shamir secret sharing can use prime fields; binary extension fields are another option. Reed–Solomon codes work over finite fields, with GF(2⁸) a common byte-oriented choice. GF(2⁸) is not ordinary integer arithmetic modulo 256.

## Key takeaways

- An inverse exists exactly when the integer and modulus have greatest common divisor one.
- Bézout coefficients construct the inverse; residues modulo a prime permit division by every nonzero residue.

## Further reading

- [Extended Euclidean algorithm — Wikipedia](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
- [Modular multiplicative inverse — Wikipedia](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
