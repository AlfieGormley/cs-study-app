---
id: crypto-ecc-scalar-security
sourceLesson: crypto-asymmetric
title: Scalar multiplication and the discrete-log gap
level: intermediate
minutes: 4
summary: A public ECC point is a private scalar multiple of a specified generator.
---

Use the toy curve over remainders modulo 17 with coefficients 2 and 2. Its generator is the coordinate pair (5, 1); the preceding lesson checks that this point lies on the curve.

The magic is a rule for **adding** two points to get a third point on the curve (geometrically: draw a line through them, find where it hits the curve again, reflect). Adding a starting point to itself repeatedly is called **scalar multiplication**. On the toy curve, the multiples of the generator (5, 1) walk through every point and then repeat: the nineteenth multiple is the point at infinity, the group's "zero", so the twentieth is (5, 1) again.

```formula reference
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
In words: repeatedly adding the generator walks through the curve's points one by one until, after 19 steps, it reaches the point at infinity and the cycle starts again, so only the scalar's remainder after dividing by 19 matters.
```

This curve has 19 points **including the point at infinity**, and the generator's multiples visit every one of them.

- **Easy direction.** Given the scalar and the generator, compute the multiple. With "double-and-add" this takes only a few hundred point operations even for a 256-bit scalar.
- **Hard direction.** Given the generator and the result, find the scalar. This is the **elliptic-curve discrete logarithm problem (ECDLP)**. Curves with special weaknesses can be easier.

The security rests on that gap. With a well-chosen curve whose generator has about 2^256 multiples, the best known generic classical attack needs roughly the square root of that many steps:

```formula essential
P = k × G
W ≈ √(N)
where
P: the public key, a point on the curve
k: the private key, a secret whole-number scalar smaller than N
G: the generator point, fixed by the curve standard
×: scalar multiplication: G added to itself k times with the curve's point-addition rule
N: the order of G: how many distinct points its multiples visit, about 2^256 for a 256-bit curve
W: the work for the best generic classical attack (Pollard's rho) to recover k from P, in group operations
√: square root
≈: approximately equal to
In words: computing the public key from the private key takes a few hundred point operations, but recovering the private key from the public key takes about √(2^256) = 2^128 operations, which is why a 256-bit curve gives roughly 128-bit security.
```

In this basic ECC model the private value is a suitable nonzero scalar and the public point is its generator multiple. Actual schemes specify their own private-key representation and scalar derivation: Ed25519 derives a scalar from a seed, while X25519 processes scalar bytes according to RFC 7748. Unlike general factoring, no sub-exponential classical attack is known on appropriately selected prime-field curves, which is why the keys can be so short.

> [!analogy] Real-world analogy: A ball bouncing round a strange table
> Imagine a ball on an oddly shaped table, struck by a machine in exactly the same way every time. Knowing the starting spot and the number of strikes, you can replay them and see where it ends up. Shown only the start and the end, though, you have no good way to tell how many strikes it took except to keep striking and compare.
>
> **How it maps:** The starting spot is the generator point, each strike is one point addition, the number of strikes is the private scalar and the final spot is the public key. Double-and-add is a shortcut for taking many strikes at once, so the forward direction stays fast even for a 256-bit count.
>
> **Where it stops:** A real table is chaotic and physical; the curve group is exact arithmetic with structure. Attackers can do better than counting strikes one by one (Pollard's rho needs about the square root of the number of points), and badly chosen curves have extra structure that makes the reverse direction easier.

In practice you meet a few named curves:

- **X25519** uses the Montgomery Curve25519 form for key agreement. **Ed25519** is a signature scheme on a related Edwards curve; these names are not interchangeable algorithms. Both have standardised encodings and requirements.
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
