---
id: disc-linear-characteristic-roots
title: "Solving linear recurrences with characteristic roots"
level: intermediate
minutes: 3
summary: "Distinct characteristic roots provide exponential solutions whose weights come from base cases."
sourceLesson: disc-inclusion-recurrences
---

### Solving linear recurrences

A **linear homogeneous recurrence with constant coefficients** makes each term a fixed weighted sum of earlier terms, with nothing else added. For a genuine second-order recurrence with a nonzero second coefficient, exponential patterns are candidates. The **characteristic equation** identifies which bases work:

```formula essential
a(n) = c_1 × a(n − 1) + c_2 × a(n − 2)
r^2 = c_1 × r + c_2
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

For the recurrence with coefficients five and negative six, the characteristic roots are two and three. The starting values two and five give weight one to each exponential. Root values determine candidate growth patterns; starting values determine the mixture.

Fibonacci numbers eventually grow by a factor close to 1.618 per step. That is exponential growth, even though the recurrence uses only addition.

Naive recursive Fibonacci repeats smaller calculations and takes exponential time. Memoisation computes each index once, giving O(n) additions where n is the requested index. Exact values grow longer, so this does not imply linear bit complexity.

## Repeated roots

For the distinct-root form above, the two roots must differ and both base terms must be supplied. A nonzero double root supplies only one exponential pattern if used twice. The second independent pattern multiplies that exponential by the index:

```formula essential
a(n) = (α + β × n) × r^n
where
a(n): the nth term of a second-order linear recurrence whose characteristic equation has the same root twice
n: the position in the sequence
r: the repeated (double) root, not zero
α, β: alpha and beta, constants fixed by the first two terms
In words: A repeated nonzero characteristic root needs a second independent solution: multiply its exponential by the index. Two copies of the same exponential alone collapse into one adjustable weight.
```

## Key takeaways

- Distinct characteristic roots provide exponential solutions whose weights come from base cases.
- A nonzero repeated root needs a second solution with an extra index factor.

## Further reading

- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
