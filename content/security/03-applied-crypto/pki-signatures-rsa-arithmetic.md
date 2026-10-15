---
id: pki-signatures-rsa-arithmetic
title: RSA signing and verification arithmetic
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: The public exponent checks a toy signature by recovering the signed number modulo the modulus.
---

A signature verifier checks a message and signature against a trusted public key. The preceding units separated that verification authority from private-key signing authority.

## A toy RSA signature

The raw RSA private exponentiation resembles the RSA decryption primitive, but real signature encoding is different from encryption padding. For this arithmetic-only example, the signer raises the message's hash to the private exponent, and the signature verifier raises the signature to the public exponent and checks that the hash comes back:

```formula
s = h^d mod n
h' = s^e mod n
where
s: the signature, a whole number from 0 to n − 1
h: the message's hash, treated as a whole number smaller than n
d: the private exponent, the secret half of the RSA key; only the signer knows it
e: the public exponent, part of the public key; real keys commonly use 65,537
n: the modulus, here the product of two secret primes; part of the public key; NIST guidance uses at least 2,048 bits for RSA signature generation, rather than this toy key
h': the value the signature verifier recovers from the signature; the signature is accepted only if h' equals h
mod: modulo: the remainder after dividing by n (for example, 17 mod 5 = 2)
In words: signing raises the hash to the private power and verifying raises the signature to the public power; the two powers undo each other, so a genuine signature gives back the hash.
```

Why do the two powers undo each other? The public and private exponents multiply to a number leaving remainder one when divided by the secret totient:

```formula
n = pq
φ = (p − 1)(q − 1)
(ed) mod φ = 1
where
n: the public modulus
p: the first secret prime
q: the second secret prime, distinct from p
φ: phi (Euler's totient of n): how many numbers from 1 to n share no factor with n; computing it needs p and q, so it stays secret
e: the public exponent
d: the private exponent
mod: modulo: the remainder after division
In words: d is the number that cancels e when you count in remainders of φ; Euler's theorem (plus a short extra argument for the rare numbers that share a factor with n) then guarantees that raising any number below n to the power e and then to the power d gives the original number back, modulo n.
```

Use the classic small key, with primes 61 and 53, public exponent 17 and private exponent 2753. Suppose the message hashes to 65:

```formula
n = 61 × 53 = 3233
φ = 60 × 52 = 3120
17 × 2753 = 46,801 = 15 × 3120 + 1
s = 65^{2753} mod 3233 = 588
h' = 588^{17} mod 3233 = 65
where
n: the toy public modulus
φ: phi, the secret totient; for the chosen primes, 60 multiplied by 52
s: the signature Alice produces with her private exponent 2753
h': the value Bob recovers with the public exponent 17; it equals the hash 65, so the signature is valid
mod: modulo: the remainder after dividing by 3233
In words: 17 × 2753 is one more than a multiple of 3120, so the exponents cancel; signing 65 gives 588, and raising 588 to the 17th power modulo 3233 gives 65 back.
```

Anyone can break this tiny example by factoring n or testing candidates. Real security requires large keys and a complete specified signature scheme; public verification alone is illustrated here.

## Key takeaways
- The public exponent checks a toy signature by recovering the signed number modulo the modulus.
- The key exponents are selected to undo one another modulo the secret totient.
- Small keys and raw arithmetic illustrate correctness, never production security.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [EdDSA — RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)
- [Deterministic ECDSA — RFC 6979](https://www.rfc-editor.org/rfc/rfc6979)
