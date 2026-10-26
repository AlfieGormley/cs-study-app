---
id: disc-modular-congruence
title: "Congruence and modular arithmetic"
level: advanced
minutes: 4
summary: "Congruence means leaving the same remainder for a fixed positive modulus."
sourceLesson: disc-number-theory
---

## Modular arithmetic

Two numbers are **congruent** modulo n when they leave the same remainder after dividing by n. A 12-hour clock is the everyday example: 17:00 and 5 o'clock show the same hand position.

```formula essential
a ≡ b (mod n)   means   n | (a − b)
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

```formula essential
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

Last-digit calculations are remainder calculations modulo ten.

Repeatedly multiplying by seven gives last digits 7, 9, 3, 1, then repeats. Reducing each intermediate product keeps the information needed for the final last digit without keeping the huge full power.

Division is the exception. You can't just cancel a common factor from both sides.

Multiplying three and eight by two produces six and sixteen: the same last digit, although three and eight have different last digits. Cancellation by two modulo ten would therefore discard a real distinction.

Division means multiplying by a **modular inverse**, which exists only when the factor and modulus are coprime.

> [!analogy] Real-world analogy: A clock face
> A twelve-hour clock returns to the same position after a full turn.
>
> **How it maps:** Times separated by whole twelve-hour turns have the same residue modulo twelve. Adding hours preserves that equivalence.
>
> **Where it stops:** The residue loses the day and number of completed turns; it cannot recover elapsed time by itself.

## Key takeaways

- Congruence means leaving the same remainder for a fixed positive modulus.
- Congruence preserves sums and products, while cancellation needs an invertible factor.

## Further reading

- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
