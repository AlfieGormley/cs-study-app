---
id: disc-fermat-euler-totient
title: "Fermat, Euler and the totient"
level: advanced
minutes: 3
summary: "Fermat reduces exponents for prime moduli and nonzero residues; Euler generalises to coprime inputs."
sourceLesson: disc-number-theory
---

## Fermat and Euler

**Fermat’s little theorem** applies when the modulus is prime and does not divide the base. Raising that base to one less than the prime gives remainder one. These assumptions are essential; a zero residue has positive powers that remain zero.

```formula reference
a^{p − 1} ≡ 1 (mod p)
where
a: an integer that p does not divide
p: a prime number
≡: is congruent to: leaves the same remainder after dividing by p
mod: "modulo": remainders after dividing by p
In words: For a prime modulus and a base not divisible by that prime, raising the base to one less than the prime gives remainder one. Whole blocks of that exponent can therefore be removed.
```

That block of multiplications contributes the multiplicative identity, so removing whole blocks from a non-negative exponent preserves the remainder.

For modulus thirteen, multiplying by twelve more copies of a coprime base leaves the same remainder as before. A shorter cycle may also exist; the theorem guarantees a working period, not always the shortest one.

**Euler’s totient** counts integers from one through a positive modulus that are coprime to it. **Euler’s theorem** says that for a modulus greater than one and a coprime base, raising the base to that count gives remainder one.

```formula reference
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
In words: The totient counts integers coprime to a positive modulus. For a modulus greater than one, any coprime base raised to the totient leaves remainder one; special counting rules apply to primes and products of distinct primes.
```

The integers one, three, seven and nine are exactly those from one through ten coprime to ten, so ten’s totient is four. For a prime, every smaller positive integer is coprime, making the totient one less than the prime. This recovers Fermat’s theorem.

> [!warning] Fermat's test can be fooled
> The converse of Fermat's theorem is false: passing the test does not prove a number prime. 561 is a **Carmichael number**: composite, yet it passes Fermat's test for every base that shares no factor with it (see below). Miller–Rabin adds stronger checks; base 2 rejects 561, but a single round is not guaranteed to reject every Carmichael number.

The number 561 factors as three times eleven times seventeen. It is composite despite passing the Fermat test for every coprime base. A test result can satisfy a necessary condition without establishing primality.

## Key takeaways

- Fermat reduces exponents for prime moduli and nonzero residues; Euler generalises to coprime inputs.
- Passing Fermat’s congruence does not prove primality; Carmichael numbers are counterexamples.

## Further reading

- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Miller–Rabin primality test — Wikipedia](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
