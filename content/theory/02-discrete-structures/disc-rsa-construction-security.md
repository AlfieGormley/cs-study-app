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
2. Multiply them to get the public modulus, and compute its totient (formula below).
3. Choose a public exponent of at least 3, below the modulus, that shares no factor with the totient. The conventional choice is 65537 when it satisfies these requirements; the small example below uses 17.
4. Compute the private exponent: the inverse of the public exponent modulo the totient, with the extended Euclidean algorithm.
5. Public key: the modulus and the public exponent. Private key: the private exponent (and the two primes, kept secret).

In symbols, with a message encoded as a number smaller than the modulus:

```formula
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
In words: the modulus is the product of two secret primes; the private exponent undoes the public one modulo the totient; encrypting raises the message to e, and decrypting raises the ciphertext to d, both modulo n.
```

**Why it works**: d was chosen so that e × d is one more than a multiple of the totient. Euler's theorem then collapses all those multiples to 1:

```formula
e × d = 1 + k × φ(n)
c^d ≡ m^{e × d} (mod n)
    = m × (m^{φ(n)})^k
    ≡ m × 1^k = m (mod n)
where
e, d: the public and private exponents
n: the public modulus, the product of the two distinct secret primes
k: some whole number (whatever makes the first line true)
φ(n): Euler's totient of n
m: the message, assumed coprime to n here
c: the ciphertext, m^e mod n
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: decrypting raises m to e × d, which is 1 plus a whole number of totients; each totient's worth gives remainder 1, leaving m itself.
```

The case where the message shares a factor with the modulus also works. Modulo either prime, a message divisible by that prime remains zero through encryption and decryption. Otherwise Fermat’s theorem applies: the product of exponents is one more than a multiple of that prime minus one. The decrypted residue therefore equals the original residue modulo each prime. Since the two primes are coprime, the Chinese remainder theorem makes the result equal modulo their product as well.

A complete example with tiny primes:

```formula
p = 61, q = 53
n = 61 × 53 = 3233
φ(n) = 60 × 52 = 3120
e = 17
d = 17^{−1} mod 3120 = 2753
17 × 2753 = 46801 = 15 × 3120 + 1
c = 65^17 mod 3233 = 2790
m = 2790^2753 mod 3233 = 65
where
p, q: the two primes
n: the public modulus
φ(n): Euler's totient of n
e: the public exponent
d: the private exponent
m: the message, 65
c: the ciphertext
mod: "modulo": the remainder after dividing by the number after it
In words: with primes 61 and 53 the modulus is 3233 and the totient 3120; the inverse of 17 is 2753 (check: 17 × 2753 leaves remainder 1 mod 3120); the message 65 encrypts to 2790, and decrypting 2790 gives 65 back.
```

**Security connection:** knowing the RSA primes p and q lets an attacker compute a private exponent. However, inverting the RSA function has not been proved equivalent to factoring, and attacks can target weak encoding, key generation, side channels or protocols without factoring n. Secure RSA schemes require their own assumptions and implementation protections. Shor's algorithm would factor n on a sufficiently capable fault-tolerant quantum computer.

> [!note] Evidence gap
> No universal RSA latency or hardware attack-time estimate is supplied: this lesson has no reproducible benchmark or deployment threat model for one.

> [!warning] Textbook RSA is not secure RSA
> The bare formula above is deterministic (the same message always encrypts the same way) and malleable (multiplying ciphertexts multiplies plaintexts). Real systems use padding such as OAEP for encryption and PSS for signatures, and generate keys with a cryptographically secure RNG (`secrets`, not `random`). Never implement RSA yourself for production use.

Implementations use the **Chinese remainder theorem** to decrypt: compute modulo each prime separately (with half-size numbers) and combine, which reduces operand sizes and can accelerate decryption; the speedup depends on arithmetic, hardware and implementation. Finite-field Diffie–Hellman uses modular exponentiation. Recovering its shared secret from public group elements is the computational Diffie–Hellman problem; solving discrete logarithms would solve it, but the two hardness assumptions are not known to be equivalent. Authentication and the full protocol introduce additional requirements.

## Key takeaways

- The private exponent reverses the public exponent modulo the totient in this construction.
- Raw RSA is deterministic and malleable; secure schemes need encoding, randomness and implementation protections.

## Further reading

- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [PKCS #1: RSA Cryptography Specifications — RFC 8017](https://www.rfc-editor.org/rfc/rfc8017.html)
