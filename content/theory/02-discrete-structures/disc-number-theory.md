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

Everything starts with whole-number division with a remainder, the kind you learned before decimals. Dividing any integer by a positive integer gives exactly one quotient and one remainder, as long as the remainder is required to lie between 0 and the divisor:

```formula
a = q × n + r
0 ≤ r < n
r = a mod n
where
a: the integer being divided (it may be negative)
n: the divisor, also called the modulus: a positive integer
q: the quotient: how many whole times n fits into a, rounding down
r: the remainder, always from 0 up to n − 1
mod: "modulo": a mod n is the remainder r left after dividing a by n
≤: is less than or equal to
<: is less than
In words: any integer a can be written as a whole number of n's plus a leftover r between 0 and n − 1, and that leftover is a mod n.
```

For example, 17 = 3 × 5 + 2, so 17 mod 5 = 2. For a negative number the quotient rounds down, not towards zero: −7 = (−3) × 3 + 2, so −7 mod 3 = 2, because the remainder can never be negative. In Python, `divmod(a, n)` returns the pair (q, r).

> [!warning] Negative numbers differ by language
> Python's `%` follows the rule above, so `-7 % 3` is `2` (and `-7 // 3` is `-3`). Modern C/C++, Java and Go integer division truncates towards zero. JavaScript Number division is floating-point, but its remainder also gives `-7 % 3 == -1` (BigInt division truncates). A negative remainder may be an invalid index. For a positive modulus use Java `Math.floorMod`, or compute `r = a % n` and add `n` only when `r < 0`. Unconditionally adding `n` in `((a % n) + n) % n` can overflow a fixed-width signed integer.

## Modular arithmetic

Two numbers are **congruent** modulo n when they leave the same remainder after dividing by n. A 12-hour clock is the everyday example: 17:00 and 5 o'clock show the same hand position.

```formula
a ≡ b (mod n)
n | (a − b)
17 ≡ 5 (mod 12)
where
a, b: integers
n: the modulus, a positive integer (12 for a clock)
≡: "is congruent to": the two sides leave the same remainder after dividing by n
mod: "modulo": names the number n that the congruence is about
|: "divides": n | x means x is a whole multiple of n (no remainder)
In words: a is congruent to b modulo n exactly when n divides their difference, which is the same as both leaving the same remainder. 17 − 5 = 12, a multiple of 12, so 17 ≡ 5 (mod 12).
```

This is the equivalence relation from the relations lesson, and its classes are the n residues 0, 1, …, n − 1: every integer is congruent to exactly one of them.

Congruence plays nicely with addition and multiplication. If you swap a number for anything congruent to it, sums and products stay congruent:

```formula
if a ≡ a′ and b ≡ b′ (mod n) then
a + b ≡ a′ + b′ (mod n)
a × b ≡ a′ × b′ (mod n)
where
a, b: integers
a′, b′: any integers congruent to a and b (for example their remainders)
n: the modulus, a positive integer
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": the congruence is about remainders after dividing by n
In words: to find the remainder of a sum or product, you may first replace each number by its remainder, then add or multiply.
```

For example, the last digit of 17 × 23 is the last digit of 7 × 3 = 21, which is 1; indeed 17 × 23 = 391.

So you can **reduce at every step**. This is how you compute huge expressions without huge numbers, and how fixed-width hardware arithmetic works: unsigned 64-bit arithmetic in C/C++ wraps modulo 2⁶⁴. Other languages may use checked arithmetic or wider integers; signed C/C++ overflow is not defined as modular wraparound.

Here is the trick on the last digit of 7¹⁰⁰ (the last digit is the remainder mod 10). Reduce after each multiplication until the powers repeat:

```formula
7^1 ≡ 7 (mod 10)
7^2 = 49 ≡ 9 (mod 10)
7^3 ≡ 9 × 7 = 63 ≡ 3 (mod 10)
7^4 ≡ 3 × 7 = 21 ≡ 1 (mod 10)
7^100 = (7^4)^25 ≡ 1^25 = 1 (mod 10)
where
7^k: k copies of 7 multiplied together (here k is 1, 2, 3, 4 or 100)
≡: is congruent to: leaves the same remainder after dividing by 10
mod: "modulo": the remainders are after dividing by 10, which gives the last digit
In words: the last digit of the powers of 7 cycles 7, 9, 3, 1, and 100 is a whole number of 4-step cycles, so 7^100 ends in 1.
```

Division is the exception. You can't just cancel a common factor from both sides:

```formula
2 × 3 = 6 ≡ 16 = 2 × 8 (mod 10)
3 ≢ 8 (mod 10)
where
≡: is congruent to: leaves the same remainder after dividing by 10
≢: is not congruent to: leaves a different remainder
mod: "modulo": remainders after dividing by 10
In words: 2 × 3 and 2 × 8 have the same last digit, but 3 and 8 don't, so you can't divide both sides by 2 modulo 10.
```

"Dividing by a" means multiplying by an **inverse** of a, which only sometimes exists (see below).

## Greatest common divisor and Euclid's algorithm

For two integers, not both zero, the **greatest common divisor** (gcd) is the largest positive whole number that divides both. Euclid's algorithm (about 300 BC, and still the one we use) rests on one fact: replacing the larger number by its remainder after dividing by the smaller one doesn't change the gcd.

```formula
gcd(a, b) = gcd(b, a mod b)
252 = 2 × 105 + 42
105 = 2 × 42 + 21
42 = 2 × 21 + 0
gcd(252, 105) = gcd(21, 0) = 21
where
gcd(a, b): the greatest common divisor of a and b: the largest positive integer dividing both
a, b: non-negative integers, not both zero
mod: "modulo": a mod b is the remainder after dividing a by b
In words: keep replacing the pair by (smaller number, remainder) until the remainder is 0; the last nonzero number is the gcd. For 252 and 105 the steps give remainders 42, 21, 0, so the gcd is 21.
```

Why it works: a mod b is a − q × b for the quotient q, so any number that divides both a and b also divides the remainder, and vice versa; the two pairs have exactly the same common divisors. We use the programming convention gcd(0, 0) = 0.

```python
def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
```

For positive inputs, Euclid's algorithm uses O(1 + log min(a, b)) remainder steps; one operand zero is an immediate case. This counts arithmetic operations, not their growing bit cost. The worst case is consecutive Fibonacci numbers, as Lamé showed in 1844. For 2048-bit numbers that is a few thousand iterations at most.

## Bézout and the extended algorithm

**Bézout's identity** says the gcd can always be built from the two numbers by multiplying each by some integer (possibly negative) and adding:

```formula
a × x + b × y = gcd(a, b)
240 × (−9) + 46 × 47 = 2
where
a, b: the two integers
x, y: the Bézout coefficients: integers, one usually negative, that the extended algorithm finds
gcd(a, b): the greatest common divisor of a and b
In words: some whole-number combination of a and b equals their gcd. For 240 and 46, whose gcd is 2, the combination is −9 lots of 240 plus 47 lots of 46: −2160 + 2162 = 2.
```

The extended Euclidean algorithm finds x and y by tracking how each remainder is built from a and b. This recursive teaching version accepts non-negative integers; large worst-case inputs can exceed Python's recursion limit, so use an iterative implementation for those cases:

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

The **modular inverse** of a modulo n is the number that multiplies a to give 1, in remainder arithmetic. It plays the role that 1/a plays for ordinary fractions:

```formula
a × a^{−1} ≡ 1 (mod n)
a × x + n × y = 1
a × x ≡ 1 (mod n)
where
a: the integer you want to "divide by"
n: the modulus, a positive integer
a^{−1}: the inverse of a modulo n, a number from 1 to n − 1 (not the fraction 1/a)
x, y: Bézout coefficients from the extended Euclidean algorithm
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: an inverse exists exactly when a and n share no common factor (their gcd is 1, called coprime). Then Bézout gives a × x + n × y = 1, and since n × y is a multiple of n, a × x leaves remainder 1, so x is the inverse.
```

Worked example: the inverse of 7 modulo 40.

```formula
7 × (−17) + 40 × 3 = 1
7^{−1} ≡ −17 ≡ −17 + 40 = 23 (mod 40)
7 × 23 = 161 = 4 × 40 + 1
where
7^{−1}: the inverse of 7 modulo 40
≡: is congruent to: leaves the same remainder after dividing by 40
mod: "modulo": remainders after dividing by 40
In words: the extended algorithm gives −17 as the coefficient of 7; adding 40 makes it positive, 23, and 7 × 23 = 161 really does leave remainder 1 when divided by 40.
```

If the gcd is bigger than 1 there is no inverse: 6 has none modulo 10, because every multiple of 6 is even and so leaves an even remainder, never 1. Python 3.8+ does this for you: `pow(7, -1, 40)` returns `23`, and raises `ValueError` if no inverse exists.

When the modulus is a prime, every nonzero residue has an inverse. That makes the residues modulo a prime a field: addition, subtraction and multiplication are defined, and division by nonzero residues is possible. Elliptic curves and Shamir secret sharing can use prime fields; binary extension fields are another option. Reed–Solomon codes work over finite fields, with GF(2⁸) a common byte-oriented choice. GF(2⁸) is not ordinary integer arithmetic modulo 256.

## Primes

A **prime number** has exactly two positive divisors, 1 and itself. The **fundamental theorem of arithmetic** says every integer above 1 factors into primes in exactly one way (up to order). There are infinitely many primes (Euclid again), and the **prime number theorem** says how common they are:

```formula
π(x) ≈ x / ln(x)
1 / ln(2^1024) ≈ 1 / 710
2 × (1 / 710) ≈ 1 / 355
where
π(x): the prime-counting function: how many primes there are up to x (here π does not mean 3.14159)
x: a large positive number
ln: the natural logarithm, log to base e ≈ 2.718; ln(2^1024) = 1024 × ln(2) ≈ 709.8
≈: is approximately equal to (the approximation improves as x grows)
In words: about 1 in ln(x) numbers near x are prime. Near 2^1024 that is about 1 in 710, and if you only try odd numbers your odds double to about 1 in 355.
```

So a random 1024-bit odd number is prime with probability roughly 1 in 355. That is why generating RSA primes by "pick random, test, repeat" is quick: a few hundred tries on average.

### Finding and testing primes

- **Trial division**: try every divisor up to the square root of the number (a factor above the square root would need a partner below it). Fine for small numbers, hopeless for 300-digit numbers.
- **Sieve of Eratosthenes**: list all primes up to a limit N in O(N log log N) time by crossing out multiples of each prime.

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

- **Miller–Rabin**: a probabilistic test. For a fixed odd composite number, each round with an independently, uniformly chosen base wrongly reports "probably prime" with probability at most 1/4. OpenSSL documents trial division followed by Miller–Rabin rounds; its round policy is version-dependent.

The rounds are independent, so their failure chances multiply:

```formula
P_false ≤ (1/4)^k
(1/4)^40 = 2^{−80} ≈ 8.3 × 10^{−25}
where
P_false: the probability that a fixed composite number passes every round
k: the number of independent rounds, here 40
≤: is less than or equal to
≈: is approximately equal to
In words: each round lets a composite slip through at most a quarter of the time, so 40 rounds let it through at most 1 time in 2^80.
```

This is a conditional false-pass bound for one given composite, not the probability that a number which passed is composite (that also depends on how candidates are chosen).

Testing primality is easy; **factoring** a product of two large primes is believed to be hard. Factoring an RSA modulus breaks its private-key protection, but hardness of factoring alone is not a proof that every RSA-based scheme is secure.

## Fast modular exponentiation

Computing a power modulo n by multiplying the base by itself once per unit of the exponent is impossible when the exponent has 600 digits. **Square-and-multiply** uses the binary digits of the exponent instead: square repeatedly to get the base to the powers 1, 2, 4, 8, …, and multiply together the ones whose bit is 1, reducing mod n after each step.

```formula
13 = 8 + 4 + 1 = 1101_2
3^13 = 3^8 × 3^4 × 3^1
3^1 ≡ 3, 3^2 ≡ 2 (mod 7)
3^4 ≡ 4, 3^8 ≡ 2 (mod 7)
3^13 ≡ 2 × 4 × 3 = 24 ≡ 3 (mod 7)
where
1101_2: the number 13 written in binary (base 2): 1 eight, 1 four, 0 twos, 1 one
3^k: k copies of 3 multiplied together
≡: is congruent to: leaves the same remainder after dividing by 7
mod: "modulo": remainders after dividing by 7
In words: write 13 in binary, get 3 to the powers 1, 2, 4, 8 by squaring (reducing mod 7 each time), and multiply the ones for the 1-bits: the answer is 3.
```

Each bit of the exponent costs one squaring, plus one extra multiplication if the bit is 1, so the work grows with the number of bits, not the size of the exponent:

```formula
M ≤ 2 × b
b ≈ log_2(e)
where
M: the number of modular multiplications square-and-multiply needs
b: the number of bits in the exponent e
e: the exponent
log_2: logarithm to base 2: how many times you can halve e before reaching 1
≤: is less than or equal to
≈: is approximately equal to
In words: the cost is at most two multiplications per bit, so a 600-digit (about 2,000-bit) exponent needs at most about 4,000 multiplications instead of 10^600.
```

So square-and-multiply needs O(log e) multiplications, where e is the exponent.

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

Tracing `modpow(3, 13, 7)`: the bits of 13 are read from the lowest, `a` is the current square of the base mod 7, and `result` is the running product:

```
bit  a   result
1    3   3
0    2   3
1    4   5
1    2   3   -> 3
```

Python's built-in `pow(a, e, n)` performs efficient modular exponentiation and also supports invertible negative exponents. The teaching routine above is for a non-negative exponent and a positive modulus and is not constant-time cryptographic code.

## Fermat and Euler

**Fermat's little theorem** tells you what happens when you raise a number to the power one less than a prime:

```formula
a^{p − 1} ≡ 1 (mod p)
where
a: an integer that p does not divide
p: a prime number
≡: is congruent to: leaves the same remainder after dividing by p
mod: "modulo": remainders after dividing by p
In words: if p is prime and does not divide a, then a to the power p − 1 leaves remainder 1 when divided by p.
```

So exponents can be reduced modulo p − 1: every block of p − 1 in the exponent contributes a factor of 1. For example, the remainder of 3²⁰⁰ divided by 13:

```formula
3^12 ≡ 1 (mod 13)
200 = 16 × 12 + 8
3^200 = (3^12)^16 × 3^8 ≡ 3^8 (mod 13)
3^8 = 6561 = 504 × 13 + 9 ≡ 9 (mod 13)
where
3^k: k copies of 3 multiplied together
≡: is congruent to: leaves the same remainder after dividing by 13
mod: "modulo": remainders after dividing by 13
In words: 13 is prime, so 3^12 leaves remainder 1; 200 is sixteen 12s plus 8, so 3^200 leaves the same remainder as 3^8, which is 9.
```

(Here 3³ = 27 already leaves remainder 1 when divided by 13, which gives the same answer faster: 200 = 66 × 3 + 2, and 3² = 9.)

**Euler's totient** counts how many of the numbers from 1 to n share no common factor greater than 1 with n. **Euler's theorem** generalises Fermat to any modulus:

```formula
φ(p) = p − 1
φ(p × q) = (p − 1) × (q − 1)
a^{φ(n)} ≡ 1 (mod n)   when gcd(a, n) = 1
where
φ(n): phi of n, Euler's totient: how many integers from 1 to n have gcd 1 with n
p, q: distinct primes
n: a positive integer modulus
a: an integer coprime to n (sharing no factor with it)
gcd(a, n): the greatest common divisor of a and n
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: a prime p has p − 1 numbers below it coprime to it; a product of two distinct primes has (p − 1) × (q − 1); and any a coprime to n, raised to the power φ(n), leaves remainder 1.
```

For example, the numbers from 1 to 10 coprime to 10 are 1, 3, 7 and 9, so the totient of 10 is 4, matching (2 − 1) × (5 − 1) = 4. And 3⁴ = 81, which leaves remainder 1 when divided by 10, as Euler's theorem predicts. For a prime modulus the totient is p − 1, so Euler's theorem becomes Fermat's.

> [!warning] Fermat's test can be fooled
> The converse of Fermat's theorem is false: passing the test does not prove a number prime. 561 is a **Carmichael number**: composite, yet it passes Fermat's test for every base that shares no factor with it (see below). Miller–Rabin adds stronger checks; base 2 rejects 561, but a single round is not guaranteed to reject every Carmichael number.

```formula
561 = 3 × 11 × 17
a^560 ≡ 1 (mod 561)   when gcd(a, 561) = 1
2^560 ≡ 1 (mod 561)
where
a: any integer that shares no factor with 561
gcd(a, 561): the greatest common divisor of a and 561
≡: is congruent to: leaves the same remainder after dividing by 561
mod: "modulo": remainders after dividing by 561
In words: 561 is not prime, but every base coprime to it behaves as Fermat's theorem says a prime would, so a Fermat test can't expose it.
```

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
k: some whole number (whatever makes the first line true)
φ(n): Euler's totient of n
m: the message, assumed coprime to n here
c: the ciphertext, m^e mod n
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: decrypting raises m to e × d, which is 1 plus a whole number of totients; each totient's worth gives remainder 1, leaving m itself.
```

(The case where the message shares a factor with the modulus also works, via the Chinese remainder theorem.)

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
- Modular arithmetic lets you reduce after every addition and multiplication; unsigned 64-bit C/C++ arithmetic wraps modulo 2⁶⁴; other language/type rules differ. Watch out for negative `%` in C-family languages.
- Euclid's algorithm computes the gcd in a number of steps proportional to the number of digits of the smaller input; the extended version gives Bézout coefficients.
- A number has an inverse modulo the modulus exactly when they share no common factor (gcd 1); Python's `pow(a, -1, n)` finds it.
- Square-and-multiply computes a modular power in a number of multiplications proportional to the exponent's bit length; Fermat and Euler let you reduce exponents.
- RSA: the modulus is the product of two secret primes, and the private exponent is the inverse of the public exponent modulo the totient; factoring the modulus breaks the key, but secure use also depends on the scheme assumptions, encoding, randomness and implementation.

## Further reading
- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Extended Euclidean algorithm — Wikipedia](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
- [Modular multiplicative inverse — Wikipedia](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
- [Miller–Rabin primality test — Wikipedia](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [RSA (cryptosystem) — Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
