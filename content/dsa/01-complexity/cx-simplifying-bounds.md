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

- **Constants vanish.** 5n^2 = Θ(n^2). The constant 5 goes into c.
- **Sums take the maximum.** n^3 + 100n^2 + 10^6 = Θ(n^3). Lower-order terms are eventually dwarfed.
- **Log bases do not matter.** Any two logarithms of n differ only by a constant factor (shown below), so we just write O(log n).
- **Exponent bases do matter.** 3^n is not O(2^n), and neither is 4^n (shown below).
- **Polynomials beat logs, exponentials beat polynomials.** (log n)^100 = o(n^0.01) and n^100 = o(1.01^n), even though both look backwards for small n.
- **Products multiply.** If one loop runs Θ(n) times and its body costs Θ(log n), the whole is Θ(n log n).

Why log bases don't matter: the change-of-base rule turns a log in one base into a log in another by dividing by a constant.

```formula
log_a(n) = log_b(n) / log_b(a)
log_2(n) = log_10(n) / log_10(2)
log_2(n) ≈ 3.32 × log_10(n)
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
4^n = (2^2)^n = 2^{2 × n}
4^n / 2^n = 2^n
where
3^n: n copies of 3 multiplied together
2^n: n copies of 2 multiplied together
4^n: n copies of 4 multiplied together
1.5^n: n copies of 1.5 multiplied together, which grows without limit
n: the input size
In words: the ratio of two exponentials with different bases keeps growing, so no constant c can cover it and the faster one is not Big-O of the slower one.
```

> [!warning] The "=" is one-way
> f = O(g) really means "f belongs to the set of functions bounded by g". So n = O(n^2) is true but "O(n^2) = n" is meaningless, and from f = O(n^2) and g = O(n^2) you cannot conclude f = g. Some books write f ∈ O(g) (∈ means "is a member of") to make this clear.

## Key takeaways
- Constants and lower-order terms disappear when comparing eventual growth.
- Changing a logarithm base changes a constant factor.
- Changing an exponential base can change the growth class.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Asymptotic analysis — Wikipedia](https://en.wikipedia.org/wiki/Asymptotic_analysis)
