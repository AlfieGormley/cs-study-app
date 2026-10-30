---
id: crypto-elliptic-curve-points
sourceLesson: crypto-asymmetric
title: Understand points on a finite-field curve
level: intermediate
minutes: 3
summary: A finite-field elliptic curve is a group of discrete points with a specified addition rule.
---

Elliptic-curve cryptography uses a different hard problem from RSA. Start with what a valid point means before considering private scalars and public multiples.

## Elliptic-curve cryptography: the intuition

**Elliptic-curve cryptography (ECC)** gets the same security with far smaller keys: a 256-bit ECC key is roughly as strong as a 3,072-bit RSA key. Smaller public-key encodings can reduce protocol overhead; performance and certificate size also depend on the scheme and protocol.

An elliptic curve is the set of points satisfying an equation of a particular shape. Over a prime **finite field** (remainders modulo a prime), the affine points form a discrete set. Together with a special identity called the point at infinity, they form the curve group under its addition rule. The short Weierstrass form shown here requires a prime greater than 3 and nonsingular coefficients; not every coefficient pair defines a valid elliptic curve. Here is the general shape and a toy curve:

```formula essential
y^2 ≡ x^3 + ax + b (mod p)
where
x, y: the coordinates of a point, whole numbers from 0 to p − 1
a, b: constants that choose the curve; the toy curve uses a = 2 and b = 2
p: the prime the arithmetic wraps around at; the toy curve uses 17, real curves use primes of about 256 bits
mod: "modulo": all arithmetic is on remainders after dividing by p
≡: "is congruent to": both sides leave the same remainder after dividing by p
In words: a point is on the curve when the remainder of y squared matches the remainder of x cubed plus a times x plus b; over a finite field this gives a scattered set of whole-number points, not a smooth line.
```

For example, check the point (5, 1) on the toy curve modulo 17. The left side is 1 squared, which is 1. The right side is 125 + 10 + 2 = 137, and 137 is 8 lots of 17 plus 1, so it also leaves remainder 1. The two sides match, so (5, 1) is on the curve.

Point membership matters in practice. Software that accepts a received "public key" without checking that it is a valid point on the expected curve can be tricked into computing on a different, weaker curve chosen by an attacker (an invalid-curve attack). Maintained libraries are designed to perform the validation each scheme requires (X25519 is built so that most of this checking is unnecessary, though it has its own rules); hand-rolled ECC code is where these checks are most often missed.

## Key takeaways
- A finite-field elliptic curve is a group of discrete points with a specified addition rule.
- Comparable classical strengths use much smaller ECC parameters than RSA parameters.

## Further reading
- [SEC 1: elliptic-curve cryptography](https://www.secg.org/sec1-v2.pdf)
- [NIST SP 800-57: key strength estimates](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
