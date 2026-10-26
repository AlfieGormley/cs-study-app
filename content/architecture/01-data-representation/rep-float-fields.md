---
id: rep-float-fields
title: Scientific notation and floating-point fields
level: intermediate
minutes: 4
summary: Normal binary values store a sign, biased exponent and fraction.
sourceLesson: rep-floating-point
---

Fixed-width integers are exact within a bounded range and do not directly encode fractions. Some applications need a far wider magnitude range, and measurements often include fractional values. Science, graphics and machine learning need numbers that are huge, tiny and fractional, all in a fixed number of bits.

The answer is **floating point**: scientific notation in binary. The widely used **IEEE 754** standard specifies floating-point formats and arithmetic; it was first published in 1985 and revised in 2008 and 2019. Earlier floating-point designs differed in formats and arithmetic rules. IEEE 754 improved portability, though evaluation order, formats, compiler options and language APIs can still change results.

## Scientific notation in base 2

In decimal **scientific notation** you write a number as a few digits times a power of ten:

A decimal value of 6,020 can be described as 6.02 thousands. The significant digits describe the detail; the scale describes the size.

The 6.02 is the **significand**; the **exponent** three specifies the thousands scale. The point "floats" to sit after the first digit.

Binary works the same way, with powers of two. Take 6.25:

Binary 6.25 is `110.01`. Moving its point two places left gives `1.1001`; scaling that significand up by four restores the original value.

Every non-zero binary number, once normalised, starts with `1.`. For normal values in the binary interchange formats discussed here, that leading 1 is implicit and is **not stored**. Subnormals and other formats require separate rules. This "hidden bit" gives one extra bit of precision for free.

## The layout

A number is stored as three fields:

```
float (binary32):
 1 bit   8 bits      23 bits
[sign][ exponent ][  fraction  ]

double (binary64):
 1 bit  11 bits      52 bits
```

The value of a normal value can also be reconstructed using this reference relationship. Zero, subnormals, infinities and NaNs need their own rules:

```formula reference
v = (−1)^s (1.f) 2^{e − bias}
where
v: the value the bits represent
s: the sign bit: 0 for positive, 1 for negative
(−1)^s: −1 to the power s: 1 when s = 0 and −1 when s = 1, so it only sets the sign
1.f: the significand: a 1, then the binary point, then the stored fraction bits f; the leading 1 is not stored (the hidden bit)
f: the fraction field: the bits after the binary point, 23 bits in a float and 52 in a double
e: the exponent field, read as an unsigned whole number (8 bits in a float, so 0 to 255)
bias: a fixed number subtracted from e to get the true exponent: 127 for float, 1023 for double, 15 for half; for an exponent field of k bits it is 2 to the power (k − 1), minus 1
2^{e − bias}: 2 to the power of the true exponent; it slides the binary point left or right
In words: for a normal value, restore the leading one, scale the significand using the stored exponent after removing its bias, then apply the sign bit.
```

The sizes of the fields and the bias for each common format:

| Format | Exp bits | Fraction bits | Bias |
|---|---|---|---|
| half (binary16) | 5 | 10 | 15 |
| float (binary32) | 8 | 23 | 127 |
| double (binary64) | 11 | 52 | 1023 |

### Why a bias?

The exponent must be able to go negative (for numbers below 1). Rather than using two's complement for negative exponents, these IEEE formats add a fixed bias before storing the exponent as an unsigned number. For binary32, a true exponent of two is stored as 129; a true exponent of minus three is stored as 124. Decoding subtracts the bias to recover the scale.

The all-zero and all-one exponent fields have special meanings. For normal binary32 values, stored exponents run from 1 through 254 and true exponents from −126 through +127.

The payoff: for positive floats, a larger bit pattern means a larger number. Unsigned ordering of the canonical binary32/binary64 encodings agrees with numeric ordering for values with sign bit zero, excluding NaNs. Negative zero, negative numbers and NaNs require additional handling.

The sign is a separate bit, so floats are **sign-magnitude**: changing the sign of a binary32 value flips bit 31 (bit 63 for binary64).

## Key takeaways
- Normal binary values store a sign, biased exponent and fraction.
- The implicit leading one increases normal-value precision.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
