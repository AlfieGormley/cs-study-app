---
id: logp-proof-techniques-direct
title: Definitions and direct proofs
level: intermediate
minutes: 5
sourceLesson: logp-proof-techniques
summary: Unpack definitions before choosing algebraic steps.
---


Tests show that code works on the inputs you tried. A **mathematical proof** shows that a claim holds for *every* input, including the ones nobody thought of. Euler's polynomial is the classic warning:

```formula
E(n) = n^2 + n + 41
E(39) = 1521 + 39 + 41 = 1601
E(40) = 1600 + 40 + 41 = 1681 = 41 × 41
where
E(n): Euler's polynomial evaluated at n
n: a natural number (0, 1, 2, …)
n^2: n multiplied by itself
In words: E(n) is prime for every n from 0 to 39 (1601 is prime), but at n = 40 it is 41 × 41, which is not prime.
```

Forty passing tests, one false claim.

Engineers need proofs more often than they expect: to convince yourself an algorithm is correct, that a lower bound is real, that an optimisation is safe, or that a distributed protocol cannot lose data. These proof units cover the main techniques. Almost every proof you will meet is built from them.

## Start with definitions

Most proof failures start with a vague definition. A proof can only use what a term precisely means. Here are the definitions this lesson relies on, written as equations:

```formula
n = 2k
n = 2k + 1
b = a × k
r = a / b,   b ≠ 0
where
n: a whole number (an integer) being described
k: some integer, which the definition says exists. The first line says n is even, the second that n is odd
a, b: integers. In the third line "b = a × k for some integer k" is what "a divides b" means, written a ∣ b
∣: "divides": a ∣ b means b is a whole-number multiple of a (3 ∣ 12 because 12 = 3 × 4)
r: a number. The fourth line, with integers a and b, says r is rational (a fraction of whole numbers)
≠: is not equal to
In words: even means "twice some integer", odd means "twice some integer, plus one", a divides b means "b is a times some integer", and rational means "an integer over a non-zero integer".
```

| Term | Definition |
|---|---|
| n is even | n equals 2k for some integer k |
| n is odd | n equals 2k + 1 for some integer k |
| a divides b (a divides b) | b equals a times k for some integer k |
| r is rational | r equals a/b, integers a, b, b is not equal to 0 |
| p is prime | integer p is greater than 1, only positive divisors 1 and p |

(In the table, 2k and a times k mean 2 times k and a times k.) Every integer is either even or odd, and not both. We will use that fact freely.


## Direct proof

To prove an implication "if p then q" (written p implies q) directly: **assume p, then derive q** step by step, using definitions and previously proven facts.

**Claim: the sum of two odd integers is even.** Assume m and n are odd. Write each one using the definition of odd, then add them:

```formula
m = 2a + 1
n = 2b + 1
m + n = (2a + 1) + (2b + 1)
      = 2a + 2b + 2
      = 2 × (a + b + 1)
where
m, n: the two odd integers
a, b: integers with m = 2 × a + 1 and n = 2 × b + 1 (they exist because m and n are odd)
In words: the sum is 2 times the integer a + b + 1, which is exactly the definition of even.
```

Since a plus b plus 1 is an integer, m plus n is even. ∎ (The symbol ∎ marks the end of a proof.)

Note what the proof does *not* do: it never picks specific numbers. "3 plus 5 equals 8 is even" is an example, not a proof. The variables a and b stand for every possible case at once.

A second example, about divisibility, shows the same pattern of unpacking definitions. **Claim: if a divides b and b divides c, then a divides c.** Write both assumptions using the definition of divides, then substitute the first into the second:

```formula
b = aj
c = bk
  = (aj) × k
  = a(jk)
where
a, b, c: integers, with a ∣ b and b ∣ c assumed
∣: divides: x ∣ y means y = x × (some integer)
j: the integer with b = a × j (it exists because a ∣ b)
k: the integer with c = b × k (it exists because b ∣ c)
In words: c is a times the integer j × k, so by definition a divides c. For example 2 ∣ 6 and 6 ∣ 18 give 18 = 2 × 9.
```

Since j times k is an integer, a divides c. ∎

The recipe: write down what you are given, using definitions. Write down what you need to reach, using definitions. Then close the gap with algebra.


## Key takeaways
- Unpack definitions before choosing algebraic steps.
- A direct proof starts from the assumptions and reaches the goal for arbitrary values.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematical proof — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_proof)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
