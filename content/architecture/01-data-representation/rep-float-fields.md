---
id: rep-float-fields
title: Scientific notation and floating-point fields
level: intermediate
minutes: 5
summary: Normal binary values store a sign, biased exponent and fraction.
sourceLesson: rep-floating-point
---

Fixed-width integers are exact within a bounded range and do not directly encode fractions. A 64-bit integer cannot hold the mass of the Sun expressed as a whole number of kilograms (about 2 × 10^30 kilograms), nor directly represent a fractional length such as the size of a proton in metres. Science, graphics and machine learning need numbers that are huge, tiny and fractional, all in a fixed number of bits.

The answer is **floating point**: scientific notation in binary. The widely used **IEEE 754** standard specifies floating-point formats and arithmetic; it was first published in 1985 and revised in 2008 and 2019. Earlier floating-point designs differed in formats and arithmetic rules. IEEE 754 improved portability, though evaluation order, formats, compiler options and language APIs can still change results.

## Scientific notation in base 2

In decimal **scientific notation** you write a number as a few digits times a power of ten:

```formula
6,020 = 6.02 × 10^3
where
6.02: the significand: the digits of the number, with the point placed after the first one
10^3: ten to the power 3, which is 1,000; the exponent 3 says how many places the point has moved
In words: 6,020 is 6.02 thousands.
```

The 6.02 is the **significand** and the 3 is the **exponent**. The point "floats" to sit after the first digit.

Binary works the same way, with powers of two. Take 6.25:

```formula
6.25 = 110.01_2 = 4 + 2 + 1/4
6.25 = 1.1001_2 × 2^2
where
110.01_2: 6.25 written in base 2; the small 2 written below the number names the base
1.1001_2: the same bits with the binary point moved two places left, so that it sits after the first 1 (normalised)
2^2: 2 to the power 2, which is 4; multiplying by 4 undoes moving the binary point two places left
In words: 6.25 is 1.1001 in binary times four.
```

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

The value of a normal number (every value except zero, subnormals, infinities and NaN, covered below) is:

```formula
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
In words: take 1.fraction in binary, move its point by (stored exponent minus bias) places, and attach the sign.
```

The sizes of the fields and the bias for each common format:

| Format | Exp bits | Fraction bits | Bias |
|---|---|---|---|
| half (binary16) | 5 | 10 | 15 |
| float (binary32) | 8 | 23 | 127 |
| double (binary64) | 11 | 52 | 1023 |

### Why a bias?

The exponent must be able to go negative (for numbers below 1). Rather than two's complement, IEEE 754 stores **exponent + bias** as an unsigned number:

```formula
e = E + bias
e = 2 + 127 = 129
e = −3 + 127 = 124
where
e: the value stored in the exponent field, an unsigned whole number
E: the true exponent, which can be negative
bias: 127 for a float (binary32)
In words: add 127 to the true exponent before storing it, so every exponent a normal float needs, −126 to +127, is stored as a positive number from 1 to 254.
```

So for a float, a true exponent of 2 is stored as 129, and −3 as 124.

The payoff: for positive floats, a larger bit pattern means a larger number. Unsigned ordering of the canonical binary32/binary64 encodings agrees with numeric ordering for values with sign bit zero, excluding NaNs. Negative zero, negative numbers and NaNs require additional handling.

The sign is a separate bit, so floats are **sign-magnitude**: changing the sign of a binary32 value flips bit 31 (bit 63 for binary64).

## Key takeaways
- Normal binary values store a sign, biased exponent and fraction.
- The implicit leading one increases normal-value precision.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
