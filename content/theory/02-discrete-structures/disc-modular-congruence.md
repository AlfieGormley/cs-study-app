---
id: disc-modular-congruence
title: "Congruence and modular arithmetic"
level: advanced
minutes: 3
summary: "Congruence means leaving the same remainder for a fixed positive modulus."
sourceLesson: disc-number-theory
---

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

## Key takeaways

- Congruence means leaving the same remainder for a fixed positive modulus.
- Congruence preserves sums and products, while cancellation needs an invertible factor.

## Further reading

- [Modular arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
