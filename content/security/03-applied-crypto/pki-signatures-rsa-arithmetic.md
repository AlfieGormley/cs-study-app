---
id: pki-signatures-rsa-arithmetic
title: RSA signing and verification arithmetic
level: basic
minutes: 3
sourceLesson: pki-signatures
summary: The public exponent checks a toy signature by recovering the signed number modulo the modulus.
---

RSA is the oldest widely used signature algorithm, and its core arithmetic shows clearly why the public key can check a signature without being able to make one.

## A toy RSA signature

The raw RSA private exponentiation resembles the RSA decryption primitive, but real signature encoding is different from encryption padding. For this arithmetic-only example, the signer raises the message's hash to the private exponent, and the signature verifier raises the signature to the public exponent and checks that the hash comes back:

```formula essential
s = h^d mod n
h' = s^e mod n
where
s: the signature, a whole number from 0 to n − 1
h: the message's hash, treated as a whole number smaller than n
d: the private exponent, the secret half of the RSA key; only the signer knows it
e: the public exponent, part of the public key; real keys commonly use 65,537
n: the modulus, the product of two secret primes; part of the public key; NIST guidance uses at least 2,048 bits for RSA signature generation, rather than a toy key
h': the value the signature verifier recovers from the signature; the signature is accepted only if h' equals h
mod: modulo: the remainder after dividing by n (for example, 17 mod 5 = 2)
In words: signing raises the hash to the private power and verifying raises the signature to the public power; the two powers undo each other, so a genuine signature gives back the hash.
```

Notice what each side needs. The signer needs `d`. The verifier needs only the public pair `n` and `e`, and learning them does not reveal `d`, because computing `d` from them is believed to require factoring the modulus.

## Why the two powers undo each other

The key is generated so that the public and private exponents cancel when you count in remainders of a secret number that only someone who knows the two primes can compute.

```formula reference
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
In words: the private exponent is chosen so that, together with the public exponent, it leaves remainder one after dividing by a secret number that only the holder of the two primes can compute; number theory then guarantees that raising a value to one exponent and then the other returns the original value.
```

The classic textbook key uses the primes 61 and 53, giving the public modulus 3233, with public exponent 17 and private exponent 2753. If a message hashes to 65, the signature is 588; raising 588 to the 17th power and keeping the remainder after dividing by 3233 gives 65 again, so the signature verifies.

Anyone can break this tiny example by factoring 3233. Real security needs large keys and a complete, specified signature scheme with proper encoding (the next unit explains why); this lesson only illustrates the verification relationship.

## Key takeaways
- The public exponent checks a toy signature by recovering the signed number modulo the modulus.
- The key exponents are selected to undo one another modulo the secret totient.
- Small keys and raw arithmetic illustrate correctness, never production security.

## Further reading
- [RSA signature schemes — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017)
- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
