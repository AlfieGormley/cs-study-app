---
id: cx-akra-bazzi
sourceLesson: cx-recurrences
title: Uneven splits and Akra–Bazzi
level: advanced
minutes: 2
summary: Balance unequal subproblems and account for work across their scales.
---

Unequal subproblems need not have equal depths. Akra–Bazzi extends recurrence analysis to several fixed shrinking fractions and accounts for work across those scales.

## Balance the recursive structure

Use a fixed number of positive child weights and fixed fractions strictly between zero and one. Base-case costs must stay between positive constants. Choose a sufficiently large fixed base threshold so that recursive children stay in the defined domain.

The nonnegative outside work must satisfy a polynomial-growth condition: throughout the range from each child size to its parent size, it stays between fixed positive multiples of the work at the parent size. Powers of size and logarithms used here satisfy this above a suitable threshold. Arbitrary oscillations need not. The formula below uses exact fractional sizes; rounded recurrences require the extended theorem’s conditions.

```formula essential
T(n) = g(n) + Σ_{i=1}^{m} a_i T(b_i n)
Σ_{i=1}^{m} a_i (b_i)^p = 1
where
T(n): total work on input size n
g(n): work outside the children
n: input size
m: a fixed number of child groups
i: group index
a_i: fixed positive child weight for group i
b_i: fixed fraction of parent size for group i, strictly between zero and one
p: the unique balancing exponent
Σ_{i=1}^{m}: add the expression for every group from one through m
In words: balance the weighted child-size fractions to find the recursive structure's growth before adding the outside work across scales.
```

The exact integral is reference material. An integral accumulates contributions over a continuous range, much as a sum adds contributions from discrete levels. Choose a fixed base threshold above any singularity, and use constant positive costs below it:

```formula reference
T(n) = Θ(n^p(1 + I(n)))
I(n) = ∫_{n_0}^{n} g(u)/u^{p+1} du
where
T(n): total work under the stated Akra–Bazzi assumptions
n: input size above the fixed base threshold
p: the balancing exponent
I(n): the accumulated outside-work correction
n_0: a fixed positive base threshold where the integrand is defined
g(u): outside work at size u
u: integration variable representing intermediate input size
∫: integrate over the sizes from the lower limit to the upper limit
du: integrate with respect to u
Θ: a tight growth bound
In words: start with the recursive leaf growth, then include the contribution of outside work accumulated across smaller input scales.
```

For one-third and two-thirds children with linear outside work, the pieces preserve the parent's total size. Complete early levels each cost linear work; every branch still has logarithmic depth. Total work is Θ(n log n).

For one-half and one-quarter children, total size falls to three quarters each generation. With linear outside work, this gives a shrinking geometric sum and Θ(n) total work. The root already supplies the matching linear lower bound.

## Key takeaways
- Unequal fixed fractions can still have tractable growth.
- The balancing exponent describes recursion; the correction includes outside work.
- Check regularity and base cases before applying the formula.

## Further reading
- [Leighton: Akra–Bazzi assumptions and extensions](https://courses.csail.mit.edu/6.046/spring04/handouts/akrabazzi.pdf)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
