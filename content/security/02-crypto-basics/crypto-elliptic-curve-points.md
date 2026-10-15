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

```formula
y^2 = x^3 + ax + b
y^2 ≡ x^3 + 2 × x + 2 (mod 17)
1^2 ≡ 5^3 + 2 × 5 + 2 = 137 (mod 17)
137 = 8 × 17 + 1 ≡ 1 (mod 17)
where
x, y: the coordinates of a point; on the toy curve, whole numbers from 0 to 16
a, b: constants that choose the curve; here a = 2 and b = 2
mod: "modulo": all arithmetic is on remainders after dividing by the prime 17
≡: "is congruent to": both sides leave the same remainder after dividing by 17
In words: a point is on the curve when its coordinates satisfy the equation; checking (5, 1) gives 1 on the left and 137, which leaves remainder 1, on the right, so it is on the curve.
```

## Key takeaways
- A finite-field elliptic curve is a group of discrete points with a specified addition rule.
- Comparable classical strengths use much smaller ECC parameters than RSA parameters.

## Further reading
- [SEC 1: elliptic-curve cryptography](https://www.secg.org/sec1-v2.pdf)
- [NIST SP 800-57: key strength estimates](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
