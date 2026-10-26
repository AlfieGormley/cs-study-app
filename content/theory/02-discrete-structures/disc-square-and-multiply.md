---
id: disc-square-and-multiply
title: "Fast modular powers with square-and-multiply"
level: advanced
minutes: 2
summary: "Binary exponentiation uses at most two modular multiplications per exponent bit."
sourceLesson: disc-number-theory
---

## Fast modular exponentiation

Computing a huge integer power by one multiplication per unit of exponent is impractical. **Square-and-multiply** instead reads its binary digits: repeated squaring supplies powers with exponents one, two, four, eight and so on. Multiply the selected powers and reduce modulo the fixed positive modulus after every operation.

Exponent thirteen selects the powers corresponding to binary positions eight, four and one. Repeated squaring produces those powers, and reducing each result modulo seven keeps the intermediate residues small.

One iteration handles one exponent bit. It always squares the base and multiplies into the result only for a set bit, so there are at most two modular multiplications per bit. This counts operations, not CPU time: multiplication cost also depends on the modulus size.

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
