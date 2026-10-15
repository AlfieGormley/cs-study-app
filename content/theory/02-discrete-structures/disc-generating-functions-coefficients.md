---
id: disc-generating-functions-coefficients
title: "Generating functions and Catalan coefficients"
level: intermediate
minutes: 3
summary: "A generating function stores a sequence in coefficients; multiplying convolves the sequences."
sourceLesson: disc-inclusion-recurrences
---

## Generating functions

A **generating function** stores a sequence a₀, a₁, a₂, … as the coefficients of a power series:

```formula
A(x) = a_0 + a_1 × x + a_2 × x^2 + …
where
A(x): the generating function of the sequence
a_0, a_1, a_2: the terms of the sequence being stored (counts, for example)
x: a placeholder variable; x^n marks position n
…: and so on, one term for every position
In words: the number of ways for size n is stored as the number in front of x^n.
```

For the formal counting manipulations here we do not need to evaluate x; it is just a clothes line to hang the numbers on. The magic is that **multiplying two generating functions convolves the sequences**: the coefficient of xⁿ in the product adds up every way to split n into a part from the first factor and a part from the second. That is exactly how "split n into a part from here and a part from there" counts combine.

The building block is the geometric series:

```formula
1 / (1 − x) = 1 + x + x^2 + x^3 + …
where
x: the placeholder variable (as a real number the series only adds up when x is between −1 and 1, but formal counting never evaluates it)
x^2, x^3: x multiplied by itself 2 and 3 times
…: and so on forever
In words: every coefficient is 1: "one way to choose any number of something". Multiply both sides by 1 − x and every term cancels except the 1.
```

Generating functions give a way to *derive* DP algorithms and prove them correct, and with more algebra they give closed forms. For Fibonacci, use the same recurrence and initial values as the earlier linear-recurrence unit:

```formula
F(x) = x / (1 − x − x^2)
where
F(x): the generating function of the Fibonacci numbers F(0), F(1), F(2), … = 0, 1, 1, 2, 3, 5, …
x: the placeholder variable
x^2: x multiplied by itself
In words: the Fibonacci numbers are the coefficients of this fraction's series. Splitting it into partial fractions recovers the golden-ratio formula above.
```

> [!note] Catalan numbers
> The Catalan numbers 1, 1, 2, 5, 14, 42, … count balanced bracket strings (by the number of bracket pairs), ordered rooted binary-tree shapes (by the number of nodes, left/right distinguished) and, from size 1 upwards, triangulations of a convex polygon with two more vertices than the size. They satisfy a convolution recurrence, and the generating function solves to a closed form (both below). There are 14 balanced strings of 4 bracket pairs.

```formula
Cat_{n+1} = Σ Cat_i × Cat_{n−i}
Cat_n = C(2n, n) / (n + 1)
Cat_4 = C(8, 4) / 5 = 70 / 5 = 14
where
Cat_n, Cat_{n+1}, Cat_i, Cat_{n−i}, Cat_4: Catalan numbers (the subscript is the size); Cat_n counts, for example, balanced strings of n bracket pairs, with Cat_0 = 1
n: the size, a whole number 0 or more; Cat_0 is 1 for the empty bracket string
i: the summation index
Σ: sigma, "sum of": add the term after it for every i from 0 to n
C(2n, n): "2n choose n", the number of ways to choose n items from 2n
In words: a balanced string splits into a first bracket pair enclosing i pairs, followed by the other n − i pairs, which gives the convolution. The closed form gives 14 for n = 4.
```

## Key takeaways

- A generating function stores a sequence in coefficients; multiplying convolves the sequences.
- Formal series support counting without evaluating the placeholder, and Catalan numbers count recursive bracket structures.

## Further reading

- [Generating function — Wikipedia](https://en.wikipedia.org/wiki/Generating_function)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Catalan number — Wikipedia](https://en.wikipedia.org/wiki/Catalan_number)
