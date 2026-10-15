---
id: disc-linear-characteristic-roots
title: "Solving linear recurrences with characteristic roots"
level: intermediate
minutes: 4
summary: "Distinct characteristic roots provide exponential solutions whose weights come from base cases."
sourceLesson: disc-inclusion-recurrences
---

### Solving linear recurrences

A **linear homogeneous recurrence with constant coefficients** makes each term a fixed weighted sum of the previous terms, with nothing else added. For the second-order case, guess a solution of the form rⁿ. Substituting and dividing by rⁿ⁻² gives the **characteristic equation**:

```formula
a(n) = c_1 × a(n − 1) + c_2 × a(n − 2)
a(n) = r^n  gives  r^2 = c_1 × r + c_2
a(n) = α × r_1^n + β × r_2^n
where
a(n): the nth term of the sequence
n: the position in the sequence, a non-negative integer; the recurrence applies from 2 upwards
c_1, c_2: fixed numbers (the constant coefficients), with c_2 not zero
r: a candidate characteristic root; r^n means n copies of r multiplied together
r_1, r_2: the two different roots (solutions) of the characteristic equation
α, β: alpha and beta, constants fixed by the base cases (the first two terms)
In words: try a pure exponential, find which characteristic roots fit, then mix them to match the starting values. This form of the solution needs the two roots to be distinct.
```

A full example starts with 2 at index zero and 5 at index one:

```formula
a(n) = 5 × a(n − 1) − 6 × a(n − 2)
r^2 − 5 × r + 6 = 0
(r − 2) × (r − 3) = 0,  so r = 2, 3
a(n) = α × 2^n + β × 3^n
α + β = 2   (n = 0)
2 × α + 3 × β = 5   (n = 1)
α = 1,  β = 1
a(n) = 2^n + 3^n
where
a(n): the nth term; a(0) = 2 and a(1) = 5 are the base cases
n: the position in the sequence
r: a root of the characteristic equation
α, β: alpha and beta, the constants fixed by the base cases
In words: the roots are 2 and 3, the two starting values force both constants to be 1, and the answer is 2^n + 3^n. Check: a(2) = 5 × 5 − 6 × 2 = 13 = 4 + 9.
```

Fibonacci, where each number is the sum of the two before it, works the same way:

```formula
r^2 = r + 1
r = (1 ± √5) / 2
φ = (1 + √5) / 2 ≈ 1.618
F(n) ≈ φ^n / √5
where
r: a root of the characteristic equation of the Fibonacci recurrence
±: plus or minus: one root uses +, the other −
√: square root, so √5 ≈ 2.236
φ: phi, the golden ratio: the larger root
F(n): the nth Fibonacci number, with F(0) = 0 and F(1) = 1
≈: approximately equal to; for n ≥ 0, F(n) is φ^n / √5 rounded to the nearest whole number
In words: Fibonacci numbers grow by a factor of about 1.618 each step. F(10) = 55, and 1.618^10 / 2.236 ≈ 55.0.
```

This is why naive recursive Fibonacci, whose call count obeys a Fibonacci-like recurrence, takes exponential time, and why memoisation reduces it to O(n) additions, where n is the index of the Fibonacci number. Exact Fibonacci values grow to about 0.69 × n bits, so this is not a linear bit-complexity bound.

## Repeated roots

- **Repeated roots.** For a genuine second-order recurrence whose characteristic equation has a nonzero double root, the solution needs an extra factor of n (below).

```formula
a(n) = (α + β × n) × r^n
a(n) = (1 + n) × 2^n
where
a(n): the nth term of a second-order linear recurrence whose characteristic equation has the same root twice
n: the position in the sequence
r: the repeated (double) root, not zero
α, β: alpha and beta, constants fixed by the first two terms
In words: with a double root, α × r^n + β × r^n is really just one constant times r^n and can't fit two starting values, so the second solution is n × r^n. For a(n) = 4 × a(n − 1) − 4 × a(n − 2) with a(0) = 1 and a(1) = 4, the double root is 2 and a(n) = (1 + n) × 2^n, so a(5) = 192.
```

## Key takeaways

- Distinct characteristic roots provide exponential solutions whose weights come from base cases.
- A nonzero repeated root needs a second solution with an extra index factor.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
