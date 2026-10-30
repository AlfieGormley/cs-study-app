---
id: crypto-rsa-key-generation
sourceLesson: crypto-asymmetric
title: Build and protect a toy RSA key
level: intermediate
minutes: 4
summary: RSA key generation chooses related public and private exponents using secret primes.
---

This is arithmetic for learning, using public modulus 3233 and tiny secret primes 61 and 53. These values offer no practical security.

## RSA with small numbers

Common two-prime RSA keys with moduli of 2,048 bits or more use primes of around 1,024 bits or more each. This unit uses the two-prime construction; PKCS #1 also defines multi-prime RSA. With tiny primes we can do every step by hand; the next unit checks the same key in Python.

### 1. Key generation

1. Pick two secret primes, here 61 and 53.
2. Multiply them to get the **modulus**. This is public.
3. Compute **Euler's totient** of the modulus from the two primes. Keep it secret.
4. Choose a **public exponent** that shares no factor with the totient. Take 17.
5. Compute the **private exponent**: the number that, multiplied by the public exponent, leaves remainder 1 after dividing by the totient. The **extended Euclidean algorithm** finds it quickly.

With the toy primes that gives modulus 3233 and totient 60 × 52 = 3120. The public exponent 17 shares no factor with 3120, and the private exponent works out as 2753, because 17 × 2753 = 46,801, which is exactly 15 × 3120 + 1. The card below states the general relationships if you want them.

```formula reference
n = pq
φ(n) = (p − 1)(q − 1)
ed ≡ 1 (mod φ(n))
where
p, q: the two secret primes (real ones are about 1,024 bits or more each)
n: the modulus, the product of the primes; part of the public key
φ: Euler's totient function: φ(n) counts the whole numbers from 1 to n that share no factor with n; for a product of two distinct primes it equals (p − 1)(q − 1)
e: the public exponent, which must share no factor with φ(n)
d: the private exponent, the modular inverse of e
mod: "modulo": arithmetic on remainders after dividing by the number that follows
≡: "is congruent to": both sides leave the same remainder after dividing by φ(n)
In words: multiply two secret primes to get the public modulus, then choose the private exponent so that public exponent times private exponent is exactly one more than a multiple of the totient.
```

That gives the two keys:

```
Public key:  (n = 3233, e = 17)
Private key: (n = 3233, d = 2753)
```

Why keep the totient secret? It is computed from the primes, and it gives them back. Knowing the modulus and the totient tells an attacker the sum of the two primes (3233 − 3120 + 1 = 114 in the toy key). Two numbers whose sum is 114 and whose product is 3233 can only be 61 and 53, found by solving a quadratic. So leaking the totient is as bad as leaking the factorisation.

The private exponent must be the inverse modulo the **totient**, not modulo the public modulus. A classic implementation bug inverts 17 modulo 3233 instead, giving 2092. That number is useless as a private exponent: with this toy key it decrypts only 4 of the 3,233 possible messages correctly. Vetted libraries avoid such mistakes. Some standards, including FIPS 186-5 for RSA signature keys, compute the private exponent modulo the Carmichael function instead (here the least common multiple of 60 and 52), which gives a smaller exponent that works equally well.

The common public exponent 65537 has binary form `1 0000 0000 0000 0001`: just two set bits. Left-to-right square-and-multiply can evaluate it with 16 squarings and one extra multiplication. Key generation still checks that it is coprime to the required modulus of exponents; primality alone does not ensure that condition. It is also far larger than tiny exponents such as 3, which make some textbook-RSA mistakes (two units later) easier to exploit.

## Key takeaways
- RSA key generation chooses related public and private exponents using secret primes.
- Knowing the totient reveals enough information to recover the two primes.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
