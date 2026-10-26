---
id: disc-euclid-bezout
title: "Euclid’s algorithm and Bézout coefficients"
level: advanced
minutes: 3
summary: "Euclid preserves common divisors while shrinking the remainder."
sourceLesson: disc-number-theory
---

## Greatest common divisor and Euclid's algorithm

For two integers, not both zero, the **greatest common divisor** (gcd) is the largest positive whole number that divides both. Euclid's algorithm (about 300 BC, and still the one we use) rests on one fact: replacing the larger number by its remainder after dividing by the smaller one doesn't change the gcd.

```formula essential
gcd(a, b) = gcd(b, a mod b)
where
gcd(a, b): the greatest common divisor of a and b: the largest positive integer dividing both
a, b: non-negative integers, not both zero; the recurrence requires b to be positive, and b equal to zero is the stopping case
mod: "modulo": a mod b is the remainder after dividing a by b
In words: Replacing the pair by divisor and remainder preserves all common divisors. Stop when the remainder is zero; the last nonzero value is the greatest common divisor.
```

Subtracting a whole multiple of the divisor leaves the remainder.

Any common divisor of the original pair divides the remainder. Conversely, a common divisor of the divisor and remainder also divides the original integer, because adding back the whole multiple reconstructs it. The two pairs therefore have exactly the same common divisors. The code uses zero for the gcd of two zeros, following the programming convention.

```python
def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        # Preserve gcd while reducing b.
        a, b = b, a % b
    return a
```

For positive inputs, the number of remainder steps grows logarithmically with the smaller input; an operand of zero is an immediate case. This counts arithmetic operations, not bit cost. Consecutive Fibonacci numbers give the worst-case pattern.

## Bézout and the extended algorithm

**Bézout's identity** says the gcd can always be built from the two numbers by multiplying each by some integer (possibly negative) and adding:

```formula essential
a × x + b × y = gcd(a, b)
where
a, b: the two integers
x, y: the Bézout coefficients: integers, one usually negative, that the extended algorithm finds
gcd(a, b): the greatest common divisor of a and b
In words: Some integer-weighted combination of two integer inputs equals their greatest common divisor. The extended Euclidean algorithm finds these weights.
```

The extended Euclidean algorithm finds x and y by tracking how each remainder is built from a and b. This recursive teaching version accepts non-negative integers; large worst-case inputs can exceed Python's recursion limit, so use an iterative implementation for those cases:

```python
def egcd(a, b):
    if b == 0:
        # Base identity: a*1 + 0*0 equals a.
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    # g = b*x + (a % b)*y
    #   = a*y + b*(x - (a//b)*y)
    return g, y, x - (a // b) * y

egcd(240, 46)   # (2, -9, 47)
# 240*(-9) + 46*47 = 2
```

## Key takeaways

- The Euclidean algorithm preserves common divisors while shrinking the remainder.
- The extended algorithm expresses the gcd as an integer combination of the inputs.

## Further reading

- [Extended Euclidean algorithm — Wikipedia](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
- [Modular multiplicative inverse — Wikipedia](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
