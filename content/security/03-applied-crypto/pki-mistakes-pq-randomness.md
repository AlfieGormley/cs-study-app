---
id: pki-mistakes-pq-randomness
title: Randomness and shared RSA factors
level: advanced
minutes: 2
sourceLesson: pki-mistakes-pq
summary: Use a CSPRNG for secret material instead of Python’s simulation-oriented random module.
---

Cryptographic security depends on the complete construction and its implementation, including key generation, message authentication and correct nonce handling.

## Mistake 3: weak randomness

Secret keys and unpredictable tokens need a **cryptographically secure** RNG. Nonces must follow the mode's contract: randomly generated nonces need a suitable CSPRNG, while modes such as GCM can also use a correctly constructed unique counter nonce.

- Python's `random` module is a Mersenne Twister. After obtaining a suitable consecutive sequence of 624 full 32-bit MT outputs, an attacker can reconstruct state and predict later generator outputs. Tokens produced through rejection sampling or truncated outputs require a different observation/recovery analysis. Use `secrets` or `os.urandom`.
- In 2008 it emerged that a 2006 Debian patch had removed nearly all entropy from OpenSSL's RNG, leaving the process ID as the only variable input. Affected OpenSSL-generated keys became predictable; the key space depended on process IDs, architecture and generation details. It was not one universal list of 32,768 keys across every key type and platform.
- In 2012, researchers computing GCDs across millions of public RSA keys could factor the keys of about 0.5% of the HTTPS hosts they scanned. Headless devices had generated keys at first boot, before collecting entropy, so different devices shared primes.

Why does a shared prime matter so much? Factoring one 2,048-bit modulus is infeasible, but finding a common factor of two is fast, using Euclid's algorithm:

```formula
n_1 = p × q_1
n_2 = p × q_2
gcd(n_1, n_2) = p   when q_1 ≠ q_2
where
n_1: the first device's public RSA modulus
n_2: the second device's public RSA modulus
p: the prime both devices happened to generate
q_1: the first device's other prime
q_2: the second device's other prime
gcd: greatest common divisor: the largest number that divides both exactly; Euclid's algorithm computes it efficiently without general-purpose factorisation
In words: two public keys that share a prime give that prime away, and dividing each modulus by it reveals the other prime, so both private keys follow.
```

With toy numbers, 3233 = 61 × 53 and 3599 = 61 × 59, so the GCD of 3233 and 3599 is 61, and both moduli factor at once. Independently sampled uniform 1,024-bit primes make accidental sharing negligible at this scale. The observed shared factors indicated severe randomness failures; the study traced many vulnerable devices to inadequate first-boot entropy.

## Key takeaways
- Use a CSPRNG for secret material instead of Python’s simulation-oriented random module.
- Weak initial entropy can cause repeated RSA primes across devices.
- A GCD of suitable distinct public moduli can reveal a shared prime without general-purpose factoring.

## Further reading
- [Cryptographic storage guidance — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST post-quantum project](https://csrc.nist.gov/projects/post-quantum-cryptography)
