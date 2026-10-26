---
id: disc-rsa-construction-security
title: "RSA construction, correctness and security limits"
level: advanced
minutes: 4
summary: "The private exponent reverses the public exponent modulo the totient in this construction."
sourceLesson: disc-number-theory
---

## RSA

Now everything fits together.

**Key generation**

1. For this mathematical two-prime construction, pick two distinct odd primes. Production key sizes and generation requirements must follow the chosen library and current deployment policy.
2. Multiply the primes to get the public modulus. Its totient is the product of one less than each prime.
3. Choose a public exponent of at least 3, below the modulus, that shares no factor with the totient. The conventional choice is 65537 when it satisfies these requirements; the small example below uses 17.
4. Compute the private exponent: the inverse of the public exponent modulo the totient, with the extended Euclidean algorithm.
5. Public key: the modulus and the public exponent. Private key: the private exponent (and the two primes, kept secret).

A message representative is an integer from zero up to, but not including, the modulus. The following reference records the construction:

```formula reference
n = p × q
φ(n) = (p − 1) × (q − 1)
gcd(e, φ(n)) = 1
d = e^{−1} mod φ(n)
c = m^e mod n
m = c^d mod n
where
p, q: two distinct secret primes
n: the public modulus
φ(n): Euler's totient of n
e: the public exponent, 3 ≤ e < n, often 65537 (not Euler's number 2.718)
d: the private exponent, the inverse of e modulo φ(n)
e^{−1}: the inverse of e: the number that multiplies e to give remainder 1
m: the message representative, an integer with 0 ≤ m < n
c: the ciphertext
gcd: greatest common divisor
mod: "modulo": the remainder after dividing by the number after it
In words: In this two-prime construction, the private exponent inverts the public exponent modulo the totient. Encryption and decryption raise the message representative and ciphertext to their respective exponents modulo the public modulus.
```

**Why it works:**

For a message coprime to the modulus, raising it by a whole totient’s worth of exponent gives remainder one. The public and private exponents multiply to one more than a multiple of the totient, so their composition leaves one copy of the message.

The case where the message shares a factor with the modulus also works. Modulo either prime, a message divisible by that prime remains zero through encryption and decryption. Otherwise Fermat’s theorem applies: the product of exponents is one more than a multiple of that prime minus one. The decrypted residue therefore equals the original residue modulo each prime. Since the two primes are coprime, the Chinese remainder theorem makes the result equal modulo their product as well.

With tiny primes 61 and 53, the public modulus is 3233. Public exponent 17 pairs with private exponent 2753 in this construction. Message 65 encrypts to 2790 and decrypts back to 65. These toy values demonstrate a round trip; they provide no security.

**Security connection:** knowing the secret prime factors lets an attacker compute a private exponent. Inverting RSA has not been proved equivalent to factoring, and attacks can instead target encoding, key generation, side channels or protocols. A sufficiently capable fault-tolerant quantum computer running Shor’s algorithm could factor the modulus.

> [!note] Evidence gap
> No universal RSA latency or hardware attack-time estimate is supplied: this lesson has no reproducible benchmark or deployment threat model for one.

> [!warning] Textbook RSA is not secure RSA
> The raw modular-power operation is deterministic (the same message always encrypts the same way) and malleable (multiplying ciphertexts multiplies message representatives modulo the public modulus). Use a vetted library with OAEP for encryption or PSS for signatures and a cryptographically secure random source. Never implement RSA yourself for production use.

Implementations use the **Chinese remainder theorem** to decrypt: compute modulo each prime separately (with half-size numbers) and combine, which reduces operand sizes and can accelerate decryption; the speedup depends on arithmetic, hardware and implementation. Finite-field Diffie–Hellman uses modular exponentiation. Recovering its shared secret from public group elements is the computational Diffie–Hellman problem; solving discrete logarithms would solve it, but the two hardness assumptions are not known to be equivalent. Authentication and the full protocol introduce additional requirements.

## Key takeaways

- The private exponent reverses the public exponent modulo the totient in this construction.
- Raw RSA is deterministic and malleable; secure schemes need encoding, randomness and implementation protections.

## Further reading

- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [PKCS #1: RSA Cryptography Specifications — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017.html)
