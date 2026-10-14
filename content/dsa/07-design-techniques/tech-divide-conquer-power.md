---
id: tech-divide-conquer-power
title: Fast and modular exponentiation
level: intermediate
minutes: 5
sourceLesson: tech-divide-conquer
summary: Compute the half-power once, then square it.
---

## Fast exponentiation

To raise a number x to a non-negative whole-number power n, straightforward powering multiplies by x one time after another, which is O(n) multiplications. The bounds here count arithmetic operations; large-integer bit costs are additional. Divide and conquer notices that a power splits into two equal halves:

```formula
x^n = (x^{n/2})^2        if n mod 2 = 0
x^n = (x^{⌊n/2⌋})^2 x  if n mod 2 = 1
where
x: the base, the number being raised to a power
n: the exponent, a whole number of at least 0
x^n: n copies of x multiplied together (x^0 = 1)
mod: the remainder after division (Python's %); n mod 2 is 0 when n is even and 1 when n is odd
(…)^2: squaring: the bracketed value multiplied by itself
⌊n/2⌋: the floor of n / 2: halve n and round down to a whole number (Python's n // 2); ⌊7/2⌋ = 3
In words: to get x to the n, compute x to half of n once and square it; if n is odd, the rounding down lost one factor of x, so multiply it back in.
```

```formula
x^7 = (x^3)^2 x
x^3 = (x^1)^2 x
where
x: the number being raised to a non-negative integer power
In words: An odd exponent leaves one extra factor after squaring the half-power.
```

```python
def power(x, n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n == 0:
        return 1
    # Reuse this result instead of calling
    # twice.
    half = power(x, n // 2)   # once!
    if n % 2 == 0:
        return half * half
    return half * half * x
```

Each call halves n, so there are about log₂n calls, each doing at most two multiplications:

```formula
T(n) = T(n / 2) + O(1) = O(log(n))
M = floor(log_2(1,000,000)) + 1 = 20
where
T(n): the number of multiplications `power` performs for exponent n
n: the exponent
O(1): a constant amount of work per call (at most two multiplications)
O(log n): grows in proportion to the logarithm of n
O: Big-O, "grows no faster than, up to a constant factor"
log: logarithm (base 2 here)
M: the exact number of squarings in the displayed recursive routine for exponent one million
floor: round down to the nearest integer
log_2(1,000,000): the base-2 logarithm of one million, about 19.93: the number of halvings from 1,000,000 down to 1
≈: approximately equal to
In words: halving the exponent each time means x to the millionth power needs about 20 squarings (plus a few extra multiplications for odd steps) instead of 999,999 multiplications.
```

> [!warning] Compute the half once
> Writing `return power(x, n // 2) * power(x, n // 2)` makes two recursive calls instead of one. You've rebuilt the slow algorithm with extra overhead.

The recurrence shows why: two calls on half the exponent, with constant work each, is the "leaves dominate" case.

```formula
T(n) = 2T(n / 2) + O(1)
c = log_2(2) = 1 > d = 0
T(n) = Θ(n^1) = Θ(n)
where
T(n): the number of multiplications for exponent n
n: the exponent
O(1): constant work per call
c: the critical exponent, log_2(a) with a = 2 subproblems
log_2(2): the base-2 logarithm of 2, which is 1
d: the exponent of the per-call work; 0 for constant work
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: the call tree doubles at every level, so it ends with about n leaves, and the total is linear in n: no better than multiplying n times.
```

The iterative version reads the bits of n from least significant upwards: square x at every step and multiply it into the result when the bit is 1.

```python
def power_iter(x, n):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    result = 1
    while n > 0:
        # A set exponent bit contributes
        # this power.
        if n & 1:
            result *= x
        # Advance to the next squared power.
        x *= x
        # Discard the exponent bit just
        # consumed.
        n >>= 1
    return result
```

With a modulus applied after every multiplication, this is **modular exponentiation**, the workhorse of RSA and Diffie–Hellman. Taking the remainder after each step keeps the numbers small, and it gives the same final remainder:

```formula
(ab) mod m
  = ((a mod m) × (b mod m)) mod m
3^13 mod 7 = 3
where
a: one number being multiplied
b: the other number being multiplied
m: the modulus, a positive whole number
mod: the remainder after dividing by m (Python's %); 17 mod 7 = 3
3^13: 3 raised to the power 13, which is 1,594,323
In words: you can reduce each factor to its remainder before multiplying and still get the right remainder at the end, so products of already-reduced non-negative residues are smaller than the square of the modulus. Reduce an initially large base before relying on that product-size bound.
```

Python’s built-in `pow(base, exp, mod)` performs efficient modular powering; CPython 3.14 uses binary powering and a sliding-window method depending on exponent size. It is not literally this loop. Fixed-size matrix powering can compute the nth Fibonacci number using O(log n) matrix multiplications, with growing integer bit costs.

## Key takeaways
- Compute the half-power once, then square it.
- Reducing products modulo a positive modulus preserves the final remainder.

## Further reading
- [Python pow](https://docs.python.org/3/library/functions.html#pow)
- [Pinned CPython 3.14 integer implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/longobject.c)
