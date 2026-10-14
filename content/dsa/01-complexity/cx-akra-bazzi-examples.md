---
id: cx-akra-bazzi-examples
sourceLesson: cx-recurrences
title: Akra–Bazzi worked examples
level: advanced
minutes: 3
summary: Apply the general method to linear selection and a gap between Master Theorem cases.
---

The previous unit introduced the balancing exponent and outside-work integral. Here n is the input size. These examples apply that method to selection and a recurrence whose outside work lies between the standard Master Theorem cases.

## Two applications

**Example 2: median of medians.** Linear-time selection has one child a fifth of the size, another seven tenths, and linear outside work:

```formula
(1/5)^1 + (7/10)^1 = 0.9 < 1
(1/5)^p + (7/10)^p = 1  gives  p ≈ 0.84
I ≈ n^{1−p} / (1 − p)
T(n) = Θ(n^p n^{1−p}) = Θ(n)
T(n) = T(n/5) + T(7n/10) + n
where
p: the balancing exponent; since the sum is below 1 at p = 1, p must be smaller than 1
I: the Akra–Bazzi integral, here ∫ of u / u^(p+1) = u^(−p) from 1 to n
T(n): the running time of median-of-medians selection on n items
n: the input size
Θ: Big-Theta, exactly this rate up to constants
≈: approximately equal to
In words: the two subproblems together are only 90% of the input, so the work per level shrinks geometrically and the root's linear work dominates.
```

**Example 3: the gap case.** Two half-size calls and linear work divided by a logarithm balance at exponent one. Use natural logarithms in the integral; changing base rescales outside work by a fixed factor:

```formula
I = ∫_2^n 1 / (u ln(u)) du = ln(ln(n)) + C
T(n) = Θ(n × (1 + ln(ln(n))))
T(n) = Θ(n log(log(n)))
T(n) = 2T(n/2) + n/log(n)
2(1/2)^1 = 1, p = 1
ln(1) = 0
where
I: the Akra–Bazzi integral with g(u) = u / ln(u) and p = 1
∫_2^n … du: the integral from 2 to n with respect to u, the area under the curve
u: a stand-in for the input size
ln: the natural logarithm (base e ≈ 2.718)
C: a constant from the lower limit, which disappears inside Θ
T(n): the running time
n: the input size
log log n: the logarithm of the logarithm of n, which grows extremely slowly (log_2 log_2 of a billion is about 5)
Θ: Big-Theta, exactly this rate up to constants
p: the balancing exponent, here one
log: any fixed logarithm base greater than one
In words: the outside work is just a log factor below n, and summed over all levels that adds only a log-log factor.
```

The integral starts at two rather than one because the logarithm at one is zero; the lower limit only changes constants.

## Key takeaways
- Subproblem fractions whose total is below one can lead to geometrically shrinking outside work.
- The integral distinguishes near-linear gap cases from the ordinary balanced case.
- A fixed lower integration limit avoids singularities without changing the growth class.

## Further reading
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
