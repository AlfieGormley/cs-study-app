---
id: pki-signatures-ecdsa-nonces
title: ECDSA and secret nonce reuse
level: basic
minutes: 4
sourceLesson: pki-signatures
summary: An ECDSA signature combines the message hash, private key and per-signature secret nonce.
---

ECDSA is an elliptic-curve signature scheme widely used in TLS certificates, passkeys and cryptocurrency wallets. Its security depends on one per-signature secret that is easy to get wrong.

## ECDSA and the nonce

ECDSA signs using an elliptic-curve key. Each signature needs a secret nonce selected according to the scheme, either securely at random or with a specified deterministic derivation. The signature is a pair of numbers:

```formula essential
r = x(kG) mod n
s = (k^{−1}(h + rd)) mod n
where
r: the first half of the signature: the x-coordinate of the curve point kG, reduced modulo n
s: the second half of the signature
k: the secret per-signature nonce, a number from 1 to n − 1; it must not leak, be biased or repeat for different messages
G: the generator: a fixed, public starting point on the elliptic curve
kG: elliptic-curve scalar multiplication: adding the point G to itself k times; easy to compute, infeasible to reverse
x: "the x-coordinate of" a point on the curve
h: the message hash, as a number (its leftmost bits if the hash is longer than n)
d: the signer's private key, a secret number; the public key is the point dG
n: the order of G, a large prime (about 2^256 for P-256)
k^{−1}: the modular inverse of k: the number that gives remainder 1 when multiplied by k, modulo n
mod: modulo: the remainder after dividing by n
In words: r is a public fingerprint of the secret nonce, and s mixes the nonce, the hash and the private key, so anyone who learns the nonce for one signature can solve s for the private key.
```

A signature verifier with the public key checks the pair without learning k or d.

The nonce is the weak point:

- **Reuse `k` for two messages** and anyone can solve two equations for `k`, then for your private key `d`. Sony's PlayStation 3 used a constant `k` for its firmware-signing key; in 2010 the fail0verflow team recovered the key and could sign anything.
- **Certain nonce biases or partial leaks** can enable private-key recovery with enough signatures; exploitability depends on the bias and observations. In 2013 a flaw in Android's `SecureRandom` let attackers steal Bitcoin from wallets that had repeated nonces.

Here is why reuse is fatal. Two signatures with the same k share the same r, and each s gives one equation. Two equations expose two unknowns: subtracting them cancels the private-key term and reveals k, and putting k back into either equation reveals d. Everything else in the equations is public.

```formula reference
s_1 k ≡ h_1 + rd   (mod n)
s_2 k ≡ h_2 + rd   (mod n)
k ≡ (h_1 − h_2) / (s_1 − s_2)   (mod n)
d ≡ (s_1 k − h_1) / r   (mod n)
where
s_1: the s half of the first signature, public
s_2: the s half of the second signature, public
h_1: the hash of the first message, public
h_2: the hash of the second message, public; it must differ from h_1
r: the r half, identical in both signatures because k repeated
k: the reused nonce, secret until this calculation
d: the private key
n: the order of the curve's generator, about 2^256 for P-256
mod: modulo: every step is done in remainders after dividing by n
/: division modulo n: multiplying by the modular inverse of the divisor
≡: congruence: both sides leave the same remainder modulo n
In words: two signatures made with the same nonce over different hashes give two equations; subtracting them reveals the nonce, and the nonce then reveals the private key, using only public values.
```

This needs the two hash values to differ (so the subtraction does not cancel to zero); signing the same message twice with the same nonce just repeats the signature and leaks nothing new.

One standard option is **deterministic ECDSA** (RFC 6979), deriving k from the private key and message hash. It removes reliance on fresh signing-time randomness, but is not a mathematical uniqueness guarantee across all messages. Secure randomness is still needed for key generation, and side-channel/fault defenses remain necessary.

## Key takeaways
- An ECDSA signature combines the message hash, private key and per-signature secret nonce.
- Reusing a nonce for suitable distinct hashes exposes the nonce and then the signing key.
- RFC 6979 derives nonces deterministically but still needs secure key generation and side-channel protection.

## Further reading
- [Deterministic ECDSA — RFC 6979](https://www.rfc-editor.org/rfc/rfc6979)
- [Elliptic Curve Digital Signature Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
