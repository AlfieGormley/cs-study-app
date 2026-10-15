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

```formula
gcd(a, b) = gcd(b, a mod b)
252 = 2 × 105 + 42
105 = 2 × 42 + 21
42 = 2 × 21 + 0
gcd(252, 105) = gcd(21, 0) = 21
where
gcd(a, b): the greatest common divisor of a and b: the largest positive integer dividing both
a, b: non-negative integers, not both zero; the recurrence requires b to be positive, and b equal to zero is the stopping case
mod: "modulo": a mod b is the remainder after dividing a by b
In words: keep replacing the pair by (smaller number, remainder) until the remainder is 0; the last nonzero number is the gcd. For 252 and 105 the steps give remainders 42, 21, 0, so the gcd is 21.
```

The remainder is the original integer minus a whole multiple of the divisor:

```formula
r = a − qb
where
a: a non-negative integer dividend
b: a positive integer divisor
q: the integer quotient, rounded down
r: the remainder, at least zero and less than b
In words: Subtracting whole copies of the divisor leaves the remainder.
```

Any common divisor of the original pair divides the remainder. Conversely, a common divisor of the divisor and remainder also divides the original integer, because adding back the whole multiple reconstructs it. The two pairs therefore have exactly the same common divisors. The code uses zero for the gcd of two zeros, following the programming convention.

```python
def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        # Preserve gcd while reducing b.
        a, b = b, a % b
    return a
```

For positive inputs, Euclid's algorithm uses O(1 + log min(a, b)) remainder steps; one operand zero is an immediate case. This counts arithmetic operations, not their growing bit cost. The worst case is consecutive Fibonacci numbers, as Lamé showed in 1844. For 2048-bit numbers that is a few thousand iterations at most.

## Bézout and the extended algorithm

**Bézout's identity** says the gcd can always be built from the two numbers by multiplying each by some integer (possibly negative) and adding:

```formula
a × x + b × y = gcd(a, b)
240 × (−9) + 46 × 47 = 2
where
a, b: the two integers
x, y: the Bézout coefficients: integers, one usually negative, that the extended algorithm finds
gcd(a, b): the greatest common divisor of a and b
In words: some whole-number combination of a and b equals their gcd. For 240 and 46, whose gcd is 2, the combination is −9 lots of 240 plus 47 lots of 46: −2160 + 2162 = 2.
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

- Euclid preserves common divisors while shrinking the remainder.
- The extended algorithm expresses the gcd as an integer combination of the inputs.

## Further reading

- [Extended Euclidean algorithm — Wikipedia](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
- [Modular multiplicative inverse — Wikipedia](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
