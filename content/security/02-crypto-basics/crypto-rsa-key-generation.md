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

Common two-prime RSA keys with moduli of 2,048 bits or more use primes of around 1,024 bits or more each. This unit uses the two-prime construction; PKCS #1 also defines multi-prime RSA. With tiny primes we can do every step by hand. (This example is checked in Python below.)

### 1. Key generation

1. Pick two secret primes, here 61 and 53.
2. Multiply them to get the **modulus**. This is public.
3. Compute **Euler's totient** of the modulus from the two primes. Keep it secret.
4. Choose a **public exponent** that shares no factor with the totient. Take 17.
5. Compute the **private exponent**: the number that, multiplied by the public exponent, leaves remainder 1 after dividing by the totient. The **extended Euclidean algorithm** finds it quickly.

```formula
n = pq = 61 × 53 = 3233
φ(n) = (p − 1)(q − 1)
φ(n) = 60 × 52 = 3120
gcd(e, φ(n)) = gcd(17, 3120) = 1
ed ≡ 1 (mod φ(n))
17 × 2753 = 46801 = 15 × 3120 + 1
where
p, q: the two secret primes, here 61 and 53 (real ones are about 1,024 bits or more each)
n: the modulus, the product of the primes; part of the public key
φ: Euler's totient function: φ(n) counts the whole numbers from 1 to n that share no factor with n; for a product of two distinct primes it equals (p − 1) × (q − 1)
e: the public exponent, here 17
gcd: greatest common divisor: the largest whole number that divides both inputs; 1 means they share no factor
d: the private exponent, here 2753: the modular inverse of e
mod: "modulo": arithmetic on remainders after dividing by the number that follows
≡: "is congruent to": both sides leave the same remainder after dividing by φ(n)
In words: multiply two primes to get the public modulus, and pick d so that e × d is exactly one more than a multiple of φ(n); here 17 × 2753 is 15 × 3120 plus 1.
```

That gives the two keys:

```
Public key:  (n = 3233, e = 17)
Private key: (n = 3233, d = 2753)
```

Why keep φ(n) secret? Expanding the totient shows that it hands over the sum of the primes:

```formula
φ(n) = (p − 1)(q − 1)
φ(n) = n − (p + q) + 1
p + q = n − φ(n) + 1
p + q = 3233 − 3120 + 1 = 114
where
φ(n): Euler's totient of the modulus, 3120 in the toy key
n: the public modulus, p × q = 3233
p, q: the secret primes
In words: anyone who knows n and φ(n) learns p + q, and two numbers whose sum is 114 and product is 3233 can only be 61 and 53 (solve the quadratic), so the factorisation falls out.
```

The common public exponent 65537 has binary form `1 0000 0000 0000 0001`: just two set bits. Left-to-right square-and-multiply can evaluate it with 16 squarings and one extra multiplication. Key generation still checks that it is coprime to the required modulus of exponents; primality alone does not ensure that condition. It is also far larger than tiny exponents such as 3, which make some textbook-RSA mistakes (below) easier to exploit.

## Key takeaways
- RSA key generation chooses related public and private exponents using secret primes.
- Knowing the totient reveals enough information to recover the two primes.

## Further reading
- [RFC 8017: RSA and OAEP](https://www.rfc-editor.org/rfc/rfc8017)
- [Python cryptography: RSA API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
