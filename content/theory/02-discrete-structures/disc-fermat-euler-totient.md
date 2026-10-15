---
id: disc-fermat-euler-totient
title: "Fermat, Euler and the totient"
level: advanced
minutes: 3
summary: "Fermat reduces exponents for prime moduli and nonzero residues; Euler generalises to coprime inputs."
sourceLesson: disc-number-theory
---

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
n: an integer modulus at least 2; the totient itself is also defined at 1 and equals 1 there
a: an integer coprime to n (sharing no factor with it)
gcd(a, n): the greatest common divisor of a and n
≡: is congruent to: leaves the same remainder after dividing by n
mod: "modulo": remainders after dividing by n
In words: a prime p has p − 1 numbers below it coprime to it; a product of two distinct primes has (p − 1) × (q − 1); and any a coprime to n, raised to the power φ(n), leaves remainder 1.
```

For example, the numbers from 1 to 10 coprime to 10 are 1, 3, 7 and 9, so the totient of 10 is 4, matching (2 − 1) × (5 − 1) = 4. And 3⁴ = 81, which leaves remainder 1 when divided by 10, as Euler's theorem predicts. For a prime modulus the totient is one less than that prime, so Euler's theorem becomes Fermat's.

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

## Key takeaways

- Fermat reduces exponents for prime moduli and nonzero residues; Euler generalises to coprime inputs.
- Passing Fermat’s congruence does not prove primality; Carmichael numbers are counterexamples.

## Further reading

- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Miller–Rabin primality test — Wikipedia](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
