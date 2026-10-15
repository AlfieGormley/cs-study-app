---
id: disc-square-and-multiply
title: "Fast modular powers with square-and-multiply"
level: advanced
minutes: 3
summary: "Binary exponentiation uses at most two modular multiplications per exponent bit."
sourceLesson: disc-number-theory
---

## Fast modular exponentiation

Computing a power modulo n by multiplying the base by itself once per unit of the exponent is impossible when the exponent has 600 digits. **Square-and-multiply** uses the binary digits of the exponent instead: square repeatedly to get the base to the powers 1, 2, 4, 8, …, and multiply together the ones whose bit is 1, reducing mod n after each step.

```formula
13 = 8 + 4 + 1 = 1101_2
3^13 = 3^8 × 3^4 × 3^1
3^1 ≡ 3, 3^2 ≡ 2 (mod 7)
3^4 ≡ 4, 3^8 ≡ 2 (mod 7)
3^13 ≡ 2 × 4 × 3 = 24 ≡ 3 (mod 7)
where
1101_2: the number 13 written in binary (base 2): 1 eight, 1 four, 0 twos, 1 one
3^k: k copies of 3 multiplied together
≡: is congruent to: leaves the same remainder after dividing by 7
mod: "modulo": remainders after dividing by 7
In words: write 13 in binary, get 3 to the powers 1, 2, 4, 8 by squaring (reducing mod 7 each time), and multiply the ones for the 1-bits: the answer is 3.
```

Each bit of the exponent costs one squaring, plus one extra multiplication if the bit is 1, so the work grows with the number of bits, not the size of the exponent:

```formula
M ≤ 2 × b
b = ⌊log_2(e)⌋ + 1   for e ≥ 1
where
M: the number of modular multiplications square-and-multiply needs
b: the number of bits in the exponent e
e: a non-negative integer exponent; zero is handled without any loop iterations
⌊ ⌋: floor: round down to the nearest integer
≥: is greater than or equal to
log_2: logarithm to base 2: how many times you can halve e before reaching 1
≤: is less than or equal to
≈: is approximately equal to
In words: the cost is at most two multiplications per bit, so a 600-digit (about 2,000-bit) exponent needs at most about 4,000 multiplications instead of 10^600.
```

For positive exponents, square-and-multiply needs O(1 + log e) multiplications, where e is the exponent. An exponent of zero returns the identity residue immediately.

```python
def modpow(a, e, n):
    if e < 0 or n <= 0:
        raise ValueError("invalid e or n")
    # Also handles modulus one and e zero.
    result = 1 % n
    a %= n
    while e:
        # Include this power for a set bit.
        if e & 1:
            result = result * a % n
        # Next bit needs the squared power.
        a = a * a % n
        # Discard the bit just processed.
        e >>= 1
    return result
```

Tracing `modpow(3, 13, 7)`: the bits of 13 are read from the lowest, `a` is the current square of the base mod 7, and `result` is the running product:

```
bit  a   result
1    3   3
0    2   3
1    4   5
1    2   3   -> 3
```

Python's built-in `pow(a, e, n)` performs efficient modular exponentiation and also supports invertible negative exponents. The teaching routine above is for a non-negative exponent and a positive modulus and is not constant-time cryptographic code.

## Key takeaways

- Binary exponentiation uses at most two modular multiplications per exponent bit.
- Reducing after each multiplication limits operand growth; the teaching implementation is not constant-time.

## Further reading

- [Built-in pow() — Python docs](https://docs.python.org/3/library/functions.html#pow)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
