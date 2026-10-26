---
id: logp-proof-techniques-direct
title: Definitions and direct proofs
level: intermediate
minutes: 5
sourceLesson: logp-proof-techniques
summary: Unpack definitions before choosing algebraic steps.
---


Tests show that code works on the inputs you tried. A **mathematical proof** shows that a claim holds for *every* input, including the ones nobody thought of. Testing a few cases is not enough over an infinite domain:

A formula can produce primes in many consecutive tests and then produce a composite number. Passing examples establish only those cases; they do not prove a claim about every natural number.

One failure is enough to refute a universal claim.

Engineers need proofs more often than they expect: to convince yourself an algorithm is correct, that a lower bound is real, that an optimisation is safe, or that a distributed protocol cannot lose data. These proof units cover the main techniques. Almost every proof you will meet is built from them.

## Start with definitions

Most proof failures start with a vague definition. A proof can only use what a term precisely means. Here are the definitions this lesson relies on, written as equations:

```formula essential
n = 2k
n = 2k + 1
b = a × k
r = a / b,   b ≠ 0
where
n: an integer, possibly negative, being described
k: some integer, which the definition says exists. The first line says n is even, the second that n is odd
a, b: integers. In the third line "b = a × k for some integer k" is what "a divides b" means, written a ∣ b
∣: "divides": a ∣ b means b is a whole-number multiple of a (3 ∣ 12 because 12 = 3 × 4)
r: a number. The fourth line, with integers a and b, says r is rational (a fraction of whole numbers)
≠: is not equal to
In words: even means "twice some integer", odd means "twice some integer, plus one", a divides b means "b is a times some integer", and rational means "an integer over a non-zero integer".
```

A prime is an integer greater than one whose only positive divisors are one and itself. Every integer is either even or odd, and not both.


## Direct proof

To prove an implication "if p then q" (written p implies q) directly: **assume p, then derive q** step by step, using definitions and previously proven facts.

**Claim: the sum of two odd integers is even.** Assume m and n are odd. Write each one using the definition of odd, then add them:

```formula essential
m = 2a + 1
n = 2b + 1
m + n = 2(a + b + 1)
where
m, n: the two odd integers
a, b: integers with m = 2 × a + 1 and n = 2 × b + 1 (they exist because m and n are odd)
In words: the sum is 2 times the integer a + b + 1, which is exactly the definition of even.
```

Since a plus b plus 1 is an integer, m plus n is even. ∎ (The symbol ∎ marks the end of a proof.)

Note what the proof does *not* do: it never picks specific numbers. "3 plus 5 equals 8 is even" is an example, not a proof. The variables a and b stand for every possible case at once.

A second example, about divisibility, shows the same pattern of unpacking definitions. **Claim: if a divides b and b divides c, then a divides c.** Follow the meaning of “integer multiple” through both assumptions:

If the first number divides the second, the second is an integer multiple of the first. If the second divides the third, the third is an integer multiple of the second. Combining those two integer multipliers gives an integer multiplier from the first number to the third.

The product of the two integer multipliers is still an integer, so the divisibility conclusion follows. ∎

The recipe: write down what you are given, using definitions. Write down what you need to reach, using definitions. Then close the gap with algebra.


## Key takeaways
- Unpack definitions before choosing algebraic steps.
- A direct proof starts from the assumptions and reaches the goal for arbitrary values.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematical proof — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_proof)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
