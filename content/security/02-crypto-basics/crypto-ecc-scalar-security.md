---
id: crypto-ecc-scalar-security
sourceLesson: crypto-asymmetric
title: Scalar multiplication and the discrete-log gap
level: intermediate
minutes: 4
summary: A public ECC point is a private scalar multiple of a specified generator.
---

Use the toy curve over remainders modulo 17 with coefficients 2 and 2. Its generator is the coordinate pair (5, 1); the preceding lesson checks that this point lies on the curve.

The magic is a rule for **adding** two points to get a third point on the curve (geometrically: draw a line through them, find where it hits the curve again, reflect). Adding a starting point to itself repeatedly is called **scalar multiplication**:

```formula
k × G = G + G + … + G
1 × G = (5, 1)
2 × G = (6, 3)
3 × G = (10, 6)
4 × G = (3, 1)
5 × G = (9, 16)
18 × G = (5, 16)
19 × G = O
where
G: the generator point, here (5, 1)
k: a whole number, the scalar: how many copies of G are added
+: point addition, the curve's chord-and-tangent rule; not ordinary addition of coordinates
×: scalar multiplication: k × G means G added to itself k times (the sum has k terms)
…: and so on, up to k copies of G
O: the point at infinity: the "zero" of point addition, so adding O to any point leaves it unchanged
In words: repeatedly adding G walks through the curve's points one by one until, after 19 steps, it reaches the point at infinity and the cycle starts again.
```

This curve has 19 points **including the point at infinity**, and G generates the group: its multiples visit every point.

- **Easy direction.** Given the scalar and G, compute the multiple. With "double-and-add" this takes only a few hundred point operations even for a 256-bit scalar.
- **Hard direction.** Given G and the result, find the scalar. This is the **elliptic-curve discrete logarithm problem (ECDLP)**. Curves with special weaknesses can be easier.

In numbers:

```formula
P = k × G
D ≈ log_2(k) ≤ 256
W ≈ √(N) ≈ √(2^256) = 2^128
where
P: the result point (in ECC, the public key)
k: the positive nonzero scalar (in ECC, the private key), smaller than the generator order, here at most a 256-bit value
G: the generator point, fixed by the curve standard
D: the number of point doublings in double-and-add (plus at most as many point additions)
log_2: the base-2 logarithm: log_2(k) is about the number of bits in k
N: the order of G: how many distinct points its multiples visit, about 2^256 for a well-chosen curve
W: the work for the best generic classical attack (Pollard's rho) to recover k from P, in group operations; the expected count depends on the variant and random-walk assumptions; the square-root order is the teaching model
√: square root
≈: approximately equal to
≤: is at most
In words: computing P from k takes a few hundred point operations, while recovering k from P takes about 2^128, which is why a 256-bit curve gives roughly 128-bit security.
```

In this basic ECC model the private value is a suitable nonzero scalar and the public point is its generator multiple. Actual schemes specify their own private-key representation and scalar derivation: Ed25519 derives a scalar from a seed, while X25519 processes scalar bytes according to RFC 7748. Unlike general factoring, no sub-exponential classical attack is known on appropriately selected prime-field curves, which is why the keys can be so short.

In practice you meet a few named curves:

- **X25519** uses the Montgomery Curve25519 form for key agreement. **Ed25519** is a signature scheme on a related Edwards curve; these names are not interchangeable algorithms. Both have standardized encodings and requirements.
- **NIST P-256** (secp256r1). A standardised NIST curve used in TLS and supported by validated implementations; approval and requirements depend on the protocol and policy.
- **secp256k1**. Used by Bitcoin and Ethereum.

ECC isn't usually used to "encrypt" directly the way RSA is. It is used for key exchange (ECDH, covered later) and signatures (ECDSA, EdDSA). Encryption to an ECC public key is done with a hybrid scheme such as ECIES or HPKE (RFC 9180).

## Key takeaways
- A public ECC point is a private scalar multiple of a specified generator.
- Generic classical discrete-log attacks require square-root work in the subgroup order.

## Further reading
- [SEC 1: elliptic-curve cryptography](https://www.secg.org/sec1-v2.pdf)
- [RFC 7748: X25519 and X448](https://www.rfc-editor.org/rfc/rfc7748)
- [NIST SP 800-57: key strength estimates](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
