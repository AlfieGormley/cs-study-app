---
id: cx-akra-bazzi
sourceLesson: cx-recurrences
title: Uneven splits and Akra–Bazzi
level: advanced
minutes: 5
summary: Balance unequal subproblems and account for work across their scales.
---

## Akra–Bazzi: the general case

The **Akra–Bazzi** method handles recurrences with several subproblem sizes under regularity assumptions: nonnegative g with suitable polynomial growth, bounded positive base cases, and sufficiently small perturbations of the subproblem sizes. The smooth polynomial/logarithmic examples here satisfy these conditions. The recurrence looks like this:

```formula
T(n) = g(n) + Σ_{i=1}^{m} a_i × T(b_i × n)
a_i > 0,  0 < b_i < 1
where
T(n): the running time on input size n
g(n): the work done outside the recursive calls (the Master Theorem's f(n))
Σ_{i=1}^{m}: capital sigma, "sum of": add up the term for every kind of subproblem i from 1 to m
m: the number of different subproblem sizes
a_i: how many subproblems of kind i each call makes, a positive constant
b_i: the fraction of n that each subproblem of kind i gets, between 0 and 1
i: which kind of subproblem
n: the input size
In words: a call does g(n) work and recurses on several groups of subproblems, each group with its own count and its own fraction of the input.
```

1. Find the unique p that balances the subproblems' total weight:

```formula
Σ_{i=1}^{m} a_i × (b_i)^p = 1
where
Σ_{i=1}^{m}: "sum of" over every kind of subproblem i from 1 to m
a_i: the number of subproblems of kind i
b_i: the fraction of the input each one gets
(b_i)^p: b_i raised to the power p
p: the unknown exponent being solved for
m: the number of kinds of subproblem
i: which kind
In words: p is the power at which the subproblems' sizes, weighted by how many there are, add up to exactly 1.
```

2. Then:

```formula
T(n) = Θ(n^p × (1 + I))
I = ∫_1^n g(u) / u^{p+1} du
where
T(n): the running time on input size n
n: the input size
p: the balancing exponent from step 1
I: an integral that measures how much the outside work g adds across all scales
∫_1^n … du: the integral from 1 to n with respect to u: the area under the curve between u = 1 and u = n, a continuous version of summing
g(u): the outside work at input size u
u: a stand-in variable for the input size, running from 1 to n
u^{p+1}: u raised to the power p + 1
Θ: Big-Theta, exactly this rate up to constants
In words: start from n^p, the cost if the leaves dominated, and multiply by a correction that grows when the outside work is comparable to or bigger than n^p.
```

The intuition: p plays the role of log_b(a). It is the exponent at which the subproblems' total "weight" exactly balances. Then you compare g with n^p, much like the Master Theorem, but the integral handles the in-between cases smoothly. (It also tolerates small perturbations such as floors and ceilings in the subproblem sizes.)

**Example 1: uneven split.** T(n) = T(n/3) + T(2n/3) + n.

```formula
(1/3)^p + (2/3)^p = 1  gives  p = 1
I = ∫_1^n u / u^2 du = ∫_1^n 1/u du = ln(n)
T(n) = Θ(n × (1 + ln(n))) = Θ(n × log n)
where
p: the balancing exponent; at p = 1 the fractions 1/3 and 2/3 add up to exactly 1
I: the Akra–Bazzi integral
∫_1^n … du: the integral from 1 to n with respect to u, the area under the curve
u: a stand-in for the input size, from 1 to n
ln(n): the natural logarithm of n (base e ≈ 2.718)
log: the logarithm in any base; it differs from ln by a constant factor
T(n): the running time
n: the input size
Θ: Big-Theta, exactly this rate up to constants
In words: the two pieces add up to the whole input, so every level does about n work, and there are about log n levels.
```

The recursion tree agrees: no level does more than n work, the first log_3(n) levels are complete and do exactly n each, and the deepest path (always taking 2/3) has log_{3/2}(n) levels (the logarithm of n to base 1.5). Both counts are Θ(log n).

## Key takeaways
- Akra–Bazzi allows different subproblem fractions under its regularity assumptions.
- The balancing exponent describes the recursive structure.
- The integral adds the contribution of outside work across scales.

## Further reading
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
