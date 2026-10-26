---
id: disc-modular-inverses
title: "Modular inverses and finite fields"
level: advanced
minutes: 2
summary: "An inverse exists exactly when the integer and modulus have greatest common divisor one."
sourceLesson: disc-number-theory
---

## Modular inverses

The **modular inverse** of a modulo n is the number that multiplies a to give 1, in remainder arithmetic. It plays the role that 1/a plays for ordinary fractions:

```formula essential
a × a^{−1} ≡ 1 (mod n)
where
a: the integer you want to "divide by"
n: the modulus, an integer at least 2 for these nonzero inverse representatives
a^{−1}: the inverse of a modulo n, a number from 1 to n − 1 (not the fraction 1/a)
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: A modular inverse multiplies a residue back to one. It exists exactly when that integer and the modulus are coprime.
```

For example, multiplying seven by twenty-three leaves remainder one modulo forty. The inverse is the residue represented by twenty-three, not the ordinary fraction one-seventh.

Bézout expresses one as an integer combination of the value and modulus whenever they are coprime. The modulus’s contribution vanishes in remainder arithmetic, leaving the value’s coefficient as an inverse.

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
