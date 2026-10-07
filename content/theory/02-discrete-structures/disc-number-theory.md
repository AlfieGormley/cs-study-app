---
id: disc-number-theory
title: Number theory for CS
level: advanced
minutes: 16
summary: Modular arithmetic, Euclid's algorithm and its extended form, modular inverses, primes and primality testing, fast exponentiation, Fermat and Euler, and how they combine into RSA.
---

Number theory underpins public-key systems such as RSA and finite-field or elliptic-curve key exchange. HTTPS can use different TLS authentication and key-exchange modes; RSA is not required for every connection. Even outside cryptography it is everywhere: hash functions, ring buffers, random number generators, checksums and consistent hashing all live in **modular arithmetic**.

This lesson builds up the handful of results that RSA needs, with an algorithm for each, so that by the end you can do RSA by hand on small numbers and understand why it works.

## Division and remainders

For integers a and n > 0 there are unique q and r with

```
a = q*n + r,   0 <= r < n
```

r is **a mod n**. In Python, `divmod(a, n)` returns (q, r).

> [!warning] Negative numbers differ by language
> Python's `%` follows the rule above, so `-7 % 3` is `2` (and `-7 // 3` is `-3`). Modern C/C++, Java and Go integer division truncates towards zero. JavaScript Number division is floating-point, but its remainder also gives -7 % 3 == -1 (BigInt division truncates). A negative remainder may be an invalid index. For a positive modulus use Java Math.floorMod, or compute r = a % n and add n only when r < 0. Unconditionally adding n in ((a % n) + n) % n can overflow a fixed-width signed integer.

## Modular arithmetic

a ≡ b (mod n) means n divides a − b: a and b leave the same remainder. This is the equivalence relation from the relations lesson, and its classes are the n residues 0, 1, …, n − 1.

Congruence plays nicely with + and ×:

```
if a ≡ a' and b ≡ b' (mod n) then
  a + b ≡ a' + b'
  a * b ≡ a' * b'
```

So you can **reduce at every step**. This is how you compute huge expressions without huge numbers, and how fixed-width hardware arithmetic works: unsigned 64-bit arithmetic in C/C++ wraps modulo 2⁶⁴. Other languages may use checked arithmetic or wider integers; signed C/C++ overflow is not defined as modular wraparound.

```
last digit of 7^100:
7^1 ≡ 7, 7^2 ≡ 9, 7^3 ≡ 3,
7^4 ≡ 1 (mod 10)
100 = 4*25, so 7^100 ≡ 1
```

Division is the exception. You can't just divide both sides: 2 · 3 ≡ 2 · 8 (mod 10), but 3 ≢ 8. "Dividing by a" means multiplying by an **inverse** of a, which only sometimes exists.

## Greatest common divisor and Euclid

For integers a and b not both zero, gcd(a, b) is their greatest positive common divisor. We use the programming convention gcd(0, 0) = 0. Euclid's algorithm (about 300 BC, and still the one we use) rests on one fact: gcd(a, b) = gcd(b, a mod b), because any common divisor of a and b also divides a − qb.

```python
def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
```

```
gcd(252, 105)
252 = 2*105 + 42
105 = 2*42  + 21
 42 = 2*21  + 0    -> 21
```

For positive inputs, Euclid uses O(1 + log min(a, b)) remainder steps; one operand zero is an immediate case. This counts arithmetic operations, not their growing bit cost. The worst case is consecutive Fibonacci numbers, as Lamé showed in 1844. For 2048-bit numbers that is a few thousand iterations at most.

## Bézout and the extended algorithm

**Bézout's identity**: for any a, b there exist integers x, y with

```
a*x + b*y = gcd(a, b)
```

The extended Euclidean algorithm finds them by tracking how each remainder is built from a and b. This recursive teaching version accepts non-negative integers; large worst-case inputs can exceed Python's recursion limit, so use an iterative implementation for those cases:

```python
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    # g = b*x + (a % b)*y
    #   = a*y + b*(x - (a//b)*y)
    return g, y, x - (a // b) * y

egcd(240, 46)   # (2, -9, 47)
# 240*(-9) + 46*47 = 2
```

## Modular inverses

The **inverse** of a mod n is a number a⁻¹ with a · a⁻¹ ≡ 1 (mod n). It exists **if and only if gcd(a, n) = 1** (a and n are coprime). When it does, Bézout gives it directly: ax + ny = 1 means ax ≡ 1 (mod n), so x is the inverse.

```
inverse of 7 mod 40:
egcd(7, 40): 7*(-17) + 40*3 = 1
so 7^-1 ≡ -17 ≡ 23 (mod 40)
check: 7 * 23 = 161 = 4*40 + 1
```

Python 3.8+ does this for you: `pow(7, -1, 40)` returns `23`, and raises `ValueError` if no inverse exists.

When n is a prime p, every a from 1 to p − 1 has an inverse. That makes the residues mod p a field: addition, subtraction and multiplication are defined, and division by nonzero residues is possible. Elliptic curves and Shamir secret sharing can use prime fields; binary extension fields are another option. Reed–Solomon codes work over finite fields, with GF(2⁸) a common byte-oriented choice. GF(2⁸) is not ordinary integer arithmetic modulo 256.

## Primes

A **prime** has exactly two positive divisors, 1 and itself. The **fundamental theorem of arithmetic** says every integer above 1 factors into primes in exactly one way (up to order). There are infinitely many primes (Euclid again), and the **prime number theorem** says about n / ln n of the numbers up to n are prime, so a random 1024-bit odd number is prime with probability roughly 1 in 355. That is why generating RSA primes by "pick random, test, repeat" is quick.

### Finding and testing primes

- **Trial division**: try divisors up to √n. Fine for small n, hopeless for 300-digit numbers.
- **Sieve of Eratosthenes**: list all primes up to N in O(N log log N) by crossing out multiples of each prime.

```python
from math import isqrt

def primes_upto(n):
    if n < 2:
        return []
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, isqrt(n) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [i for i, p in enumerate(is_p)
            if p]
```

- **Miller–Rabin**: a probabilistic test. For a fixed odd composite n, each independently uniform base from 1 through n − 1 has a false-pass probability at most 1/4, so 40 independent rounds give at most 2⁻⁸⁰. This is a conditional false-pass bound, not the posterior probability that any accepted candidate is composite. OpenSSL documents trial division followed by Miller–Rabin rounds; its round policy is version-dependent.

Testing primality is easy; **factoring** a product of two large primes is believed to be hard. Factoring an RSA modulus breaks its private-key protection, but hardness of factoring alone is not a proof that every RSA-based scheme is secure.

## Fast modular exponentiation

Computing aᵉ mod n by multiplying e times is impossible when e has 600 digits. **Square-and-multiply** uses the binary digits of e and needs only O(log e) multiplications, reducing mod n after each:

```python
def modpow(a, e, n):
    if e < 0 or n <= 0:
        raise ValueError("invalid e or n")
    result = 1 % n
    a %= n
    while e:
        if e & 1:
            result = result * a % n
        a = a * a % n
        e >>= 1
    return result
```

```
3^13 mod 7, 13 = 1101 in binary
bit  a(mod 7)  result
1    3         3
0    2         3
1    4         5
1    2         3     -> 3
```

Python's built-in pow(a, e, n) performs efficient modular exponentiation and also supports invertible negative exponents. The teaching routine above is for integer e ≥ 0 and n > 0 and is not constant-time cryptographic code.

## Fermat and Euler

**Fermat's little theorem**: if p is prime and p does not divide a, then

```
a^(p-1) ≡ 1 (mod p)
```

So exponents can be reduced mod p − 1. For example 3²⁰⁰ mod 13: 3¹² ≡ 1, and 200 = 16 · 12 + 8, so 3²⁰⁰ ≡ 3⁸ ≡ 9 (mod 13). (Here 3³ = 27 ≡ 1 already, which gives the same answer faster.)

**Euler's totient** φ(n) counts the integers from 1 to n coprime to n. For a prime, φ(p) = p − 1; for distinct primes p and q, φ(pq) = (p − 1)(q − 1). **Euler's theorem** generalises Fermat: if gcd(a, n) = 1, then a^φ(n) ≡ 1 (mod n).

> [!warning] Fermat's test can be fooled
> The converse of Fermat's theorem is false. 561 = 3 · 11 · 17 is a **Carmichael number**: a⁵⁶⁰ ≡ 1 (mod 561) for every a coprime to 561, even though 561 is composite. Miller–Rabin adds stronger checks; base 2 rejects 561, but a single round is not guaranteed to reject every Carmichael number.

## RSA

Now everything fits together.

**Key generation**

1. For this mathematical two-prime construction, pick distinct odd primes p and q. Production key sizes and generation requirements must follow the chosen library and current deployment policy.
2. n = pq and φ(n) = (p − 1)(q − 1).
3. Choose an integer 3 ≤ e < n coprime to φ(n). The conventional choice is e = 65537 when it satisfies these requirements; the small example below uses e = 17.
4. Compute d = e⁻¹ mod φ(n) with the extended Euclidean algorithm.
5. Public key (n, e). Private key d (and p, q, kept secret).

For an integer message representative 0 ≤ m < n, encrypt c = mᵉ mod n and decrypt m = c^d mod n.

**Why it works**: ed = 1 + kφ(n), so c^d = m^(ed) = m · (m^φ(n))ᵏ ≡ m (mod n) by Euler's theorem. (The case where m shares a factor with n also works, via the Chinese remainder theorem.)

```
p = 61, q = 53
n = 3233, phi = 60*52 = 3120
e = 17
d = 17^-1 mod 3120 = 2753
    (17 * 2753 = 46801
     = 15*3120 + 1)
m = 65
c = 65^17 mod 3233   = 2790
    2790^2753 mod 3233 = 65
```

**Security connection:** knowing p and q lets an attacker compute a private exponent. However, inverting the RSA function has not been proved equivalent to factoring, and attacks can target weak encoding, key generation, side channels or protocols without factoring n. Secure RSA schemes require their own assumptions and implementation protections. Shor's algorithm would factor n on a sufficiently capable fault-tolerant quantum computer.

> [!note] Evidence gap
> No universal RSA latency or hardware attack-time estimate is supplied: this lesson has no reproducible benchmark or deployment threat model for one.

> [!warning] Textbook RSA is not secure RSA
> The bare formula above is deterministic (the same message always encrypts the same way) and malleable (multiplying ciphertexts multiplies plaintexts). Real systems use padding such as OAEP for encryption and PSS for signatures, and generate keys with a cryptographically secure RNG (`secrets`, not `random`). Never implement RSA yourself for production use.

Implementations use the **Chinese remainder theorem** to decrypt: compute mod p and mod q separately (with half-size numbers) and combine, which reduces operand sizes and can accelerate decryption; the speedup depends on arithmetic, hardware and implementation. Finite-field Diffie–Hellman uses modular exponentiation. Recovering its shared secret from public group elements is the computational Diffie–Hellman problem; solving discrete logarithms would solve it, but those hardness assumptions must not simply be equated. Authentication and the full protocol introduce additional requirements.

## Key takeaways
- Modular arithmetic lets you reduce after every + and ×; unsigned C/C++ k-bit arithmetic wraps modulo 2ᵏ; other language/type rules differ. Watch out for negative `%` in C-family languages.
- Euclid's algorithm computes gcd in O(log n) steps; the extended version gives Bézout coefficients.
- a has an inverse mod n exactly when gcd(a, n) = 1; `pow(a, -1, n)` finds it.
- Square-and-multiply computes aᵉ mod n in O(log e) multiplications; Fermat and Euler let you reduce exponents.
- RSA: n = pq, d = e⁻¹ mod (p − 1)(q − 1); factoring n breaks the key, but secure use also depends on the scheme assumptions, encoding, randomness and implementation.

## Further reading
- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Extended Euclidean algorithm — Wikipedia](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
- [Modular multiplicative inverse — Wikipedia](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
- [Miller–Rabin primality test — Wikipedia](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
