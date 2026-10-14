---
id: cx-simplifying-bounds
sourceLesson: cx-asymptotic-notation
title: Simplifying asymptotic expressions
level: basic
minutes: 3
summary: Drop dominated terms while preserving distinctions between exponential bases.
---

Here n is the input size. These rules simplify a cost after the meaning of upper, lower and tight bounds is clear.

## Simplification rules

These all follow from the definitions. In each, n is the input size:

- **Constants vanish.** Fixed multipliers go into the bound’s constant.
- **Sums take the maximum.** Eventually the fastest-growing term dwarfs the others.
- **Log bases do not matter.** Any two logarithms differ by a fixed factor, so O(log n) ignores their bases.
- **Exponent bases do matter.** Cubic-base and quartic-base exponentials outgrow a base-two exponential.
- **Polynomials beat logs, exponentials beat polynomials.** The examples below hold eventually even when small inputs suggest the reverse.
- **Products multiply.** Θ(n) iterations each costing Θ(log n) give Θ(n log n) overall. Here n is the input size.

```formula
5n^2 = Θ(n^2)
n^3 + 100n^2 + 10^6 = Θ(n^3)
(log(n))^{100} = o(n^{0.01})
n^{100} = o(1.01^n)
where
n: the input size
log: the base-2 logarithm
Θ: a tight growth bound
o: little-o: grows strictly slower than the comparison
In words: Fixed coefficients and dominated terms do not change eventual growth. A fixed power of a logarithm loses to any positive power of the input, and a fixed polynomial loses to an exponential.
```

Why log bases don't matter: the change-of-base rule turns a log in one base into a log in another by dividing by a constant.

```formula
log_a(n) = log_b(n) / log_b(a)
log_2(n) = log_10(n) / log_10(2)
log_2(n) ≈ 3.32log_10(n)
where
log_a(n): the logarithm of n to base a: the power you raise a to in order to get n
log_b(n): the logarithm of n to base b
log_b(a): the logarithm of a to base b, a fixed number because a and b are fixed
log_2(n): the base-2 logarithm of n
log_10(n): the base-10 logarithm of n (log_10(1000) = 3)
a, b: any two fixed bases greater than 1
n: the input size
≈: approximately equal to
In words: switching the base of a logarithm just multiplies it by a constant, and Big-O ignores constants, so O(log_2 n) and O(log_10 n) are the same class.
```

Why exponent bases do matter: dividing one exponential by another leaves an exponential, not a constant.

```formula
3^n / 2^n = (3 / 2)^n = 1.5^n
4^n = (2^2)^n = 2^{2n}
4^n / 2^n = 2^n
where
2^n: n copies of 2 multiplied together
n: the input size
In words: the ratio of two exponentials with different bases keeps growing, so no constant c can cover it and the faster one is not Big-O of the slower one.
```

> [!warning] The "=" is one-way
> A growth class is a set of functions. Saying a function has an upper bound means membership in that set, rather than ordinary equality. Reversing that statement treats a class as a value. Two functions in the same class need not equal one another.

```formula
f ∈ O(g)
n ∈ O(n^2)
f ∈ O(n^2), g ∈ O(n^2)
f(n) = n, g(n) = n^2
f ≠ g
where
f, g: operation-count functions; the last two lines give a counterexample with f linear and g quadratic
f(n), g(n): the values of those functions at input size n
n: the positive input size; in the second line n names the linear input-size function
O: an eventual upper growth class
∈: is a member of
≠: is not equal to
In words: Membership is not equality: a linear function has a quadratic upper bound, and two functions can share a bound without having equal values.
```

An expression that incorrectly treats the class as a number is:

```formula
O(n^2) = n
where
n: the input size
O(n^2): the class of functions with a quadratic upper bound
In words: This displayed equality is invalid; it reverses a membership statement and compares a class with a value.
```

## Key takeaways
- Constants and lower-order terms disappear when comparing eventual growth.
- Changing a logarithm base changes a constant factor.
- Changing an exponential base can change the growth class.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Asymptotic analysis — Wikipedia](https://en.wikipedia.org/wiki/Asymptotic_analysis)
