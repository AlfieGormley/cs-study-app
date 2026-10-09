---
id: rep-floating-point
title: IEEE 754 floating point
level: intermediate
minutes: 15
summary: How floats and doubles are encoded bit by bit, why 0.1 + 0.2 is not 0.3, what infinities, NaNs and subnormals are for, and how to compute with floats safely.
---

Fixed-width integers are exact within a bounded range and do not directly encode fractions. A 64-bit integer cannot hold the mass of the Sun in kilograms (about 2 × 10^30), nor the size of a proton in metres. Science, graphics and machine learning need numbers that are huge, tiny and fractional, all in a fixed number of bits.

The answer is **floating point**: scientific notation in binary. Almost every processor today implements the **IEEE 754** standard, first published in 1985 and revised in 2008 and 2019. Earlier floating-point designs differed in formats and arithmetic rules. IEEE 754 improved portability, though evaluation order, formats, compiler options and language APIs can still change results.

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
v = (−1)^s × 1.f × 2^{e − bias}
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

## Worked example: encoding −6.25 as a float

1. Sign: negative, so **1**.
2. Binary: 6.25 = `110.01`.
3. Normalise: `1.1001 × 2²`.
4. Exponent: 2 + 127 = 129 = **`10000001`**.
5. Fraction: the bits after the point, `1001`, padded to 23 bits.

```
1 10000001 10010000000000000000000
```

Group into hex:

```
1100 0000 1100 1000 0000 ... 0000
   C    0    C    8    0 0 0 0
= 0xC0C80000
```

Check it by decoding with the value formula:

```formula
v = (−1)^s × 1.f × 2^{e − bias}
v = (−1)^1 × 1.1001_2 × 2^{129 − 127}
v = −1 × 1.5625 × 4 = −6.25
where
v: the value the bits represent
s: the sign bit, here 1 (negative)
1.f: the significand, here 1.1001 in binary = 1 + 1/2 + 1/16 = 1.5625
1.1001_2: the digits 1.1001 read in base 2
f: the stored fraction bits, here 1001 followed by zeros
e: the stored exponent field, here 129
bias: 127 for a float
In words: the bits decode back to −1.5625 × 4, which is −6.25.
```

You can also check it in Python:

```python
import struct
struct.pack('>f', -6.25).hex()
# 'c0c80000'
```

### Decoding works backwards

Take `0x41580000`:

```
0100 0001 0101 1000 0000 ...
0 10000010 10110000000000000000000
```

- Sign 0: positive.
- Exponent `10000010` = 130, so the true exponent is 130 − 127 = 3.
- Significand: 1 followed by the fraction bits `1011`.

```formula
v = (−1)^s × 1.f × 2^{e − bias}
v = (−1)^0 × 1.1011_2 × 2^{130 − 127}
v = 1 × 1.6875 × 2^3
v = 1.6875 × 8 = 13.5
where
v: the value the bits represent
s: the sign bit, here 0 (positive)
1.f: the significand; here 1.1011 in binary
1.1011_2: 1 + 1/2 + 1/8 + 1/16 = 1.6875
f: the stored fraction bits, here 1011 followed by zeros
e: the stored exponent field, here 130
bias: 127 for a float
2^3: 2 to the power 3, which is 8
In words: 1.6875 with its binary point moved three places right is 13.5.
```

## Why 0.1 + 0.2 != 0.3

Lesson 1 showed that 0.1 in binary is `0.000110011001100...`, repeating forever. A float must cut it off after 24 significant bits and round:

```
0.1 as float:
0 01111011 10011001100110011001101
= 0x3DCCCCCD
= 0.100000001490116119384765625
```

The last bits `...1100` became `...1101` because the discarded tail was more than half a unit, so it rounded up. As a double, 0.1 is stored as 0.1000000000000000055511151231257827... Each of 0.1, 0.2 and 0.3 is rounded to its nearest double, and the errors do not cancel:

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

This is not a bug in Python, or JavaScript, or your CPU. It is the correct IEEE 754 result: the sum of the two nearest doubles, rounded to the nearest double, which happens to be the one just above 0.3's nearest double.

## Precision and range

The significand has a fixed number of bits, so the **gap between neighbouring floats grows** with their size. Floats are dense near zero and sparse far away.

The table below uses the computer shorthand for scientific notation: `1.19e−7` means 1.19 × 10^−7 (0.000000119) and `3.40e38` means 3.40 × 10^38.

| | float | double |
|---|---|---|
| Significant bits | 24 | 53 |
| Decimal digits | about 7 | about 15–16 |
| Machine epsilon | 2^−23 ≈ 1.19e−7 | 2^−52 ≈ 2.22e−16 |
| Largest | ≈ 3.40e38 | ≈ 1.80e308 |
| Exact integers up to | 2^24 = 16,777,216 | 2^53 ≈ 9.007e15 |

**Machine epsilon** is the gap between 1.0 and the next float above it. It follows from the number of significant bits:

```formula
ε = 2^{−(p − 1)}
ε = 2^{−23} ≈ 1.19 × 10^{−7}   for p = 24
ε = 2^{−52} ≈ 2.22 × 10^{−16}   for p = 53
where
ε: epsilon, machine epsilon: the gap between 1.0 and the next larger representable value
p: the precision: the number of significant bits, including the hidden bit (24 for float, 53 for double)
2^{−23}: 1 divided by 2 to the power 23, the weight of the last fraction bit when the exponent is 0
≈: approximately equal to (rounded)
In words: the last of the 23 stored fraction bits of a float is worth about 0.000000119 when the number is near 1, so that is the smallest step up from 1.0.
```

For normal values away from zero, the gap scales with the size of the number. It is constant within each **binade** (the range from one power of two up to the next) and doubles at each power of two:

```formula
Δ = 2^E × ε   for 2^E ≤ |x| < 2^{E+1}
Δ ≈ |x| × ε
Δ = 2^24 × 2^{−23} = 2
where
Δ: delta, the gap between x and the next representable value further from zero
x: a normal floating-point value
|x|: the absolute value of x: x without its sign
E: the true exponent of x: the power of two at or just below |x|
ε: machine epsilon, 2^{−23} for float and 2^{−52} for double; the third line uses a float from 2^24 up to 2^25
≤: less than or equal to; <: less than
≈: approximately equal to
In words: between two neighbouring powers of two the gap is fixed, and it is roughly the size of the number times epsilon, so from 2^24 upwards neighbouring floats are 2 apart.
```

Subnormals have fixed absolute spacing. Two consequences:

- Above 2^24 a float cannot represent every integer. `16777217.0f` rounds to 16,777,216. Using a `float` for a counter or a timestamp silently stops counting.
- Above 2^53 a double cannot either. That is why JavaScript Number values (binary64, distinct from BigInt) have `Number.MAX_SAFE_INTEGER`, which is 2^53 − 1 (9,007,199,254,740,991); decimal strings or BigInt are alternatives for larger exact integer IDs.

Adding a small number to a big one can lose it entirely:

```python
>>> 1e16 + 1.0 - 1e16
0.0
```

The gap formula explains it:

```formula
2^53 ≤ 10^16 < 2^54
Δ = 2^53 × 2^{−52} = 2
where
2^53: about 9.007 × 10^15, the power of two just below 10^16
2^54: about 1.8 × 10^16, the next power of two
Δ: delta, the gap between neighbouring doubles in this binade
2^{−52}: machine epsilon for a double
≤: less than or equal to; <: less than
In words: 10^16 lies between 2 to the 53 and 2 to the 54, where neighbouring doubles are 2 apart.
```

So 10^16 + 1 is exactly halfway between two doubles, and it rounds back to 10^16.

## Rounding

IEEE 754's default rounding mode is **round to nearest, ties to even**. When a result is exactly halfway between two representable values, it picks the one whose last bit is 0. This avoids the upward bias of always rounding halves up.

Python's `round()` uses the same rule for halfway cases: `round(0.5)` is 0, `round(1.5)` is 2, `round(2.5)` is 2. But `round(2.675, 2)` gives 2.67, not because of ties-to-even, but because 2.675 is actually stored as 2.67499999999999982236431605997495353221893310546875.

## Special values

The all-zeros and all-ones exponents are reserved:

| Exponent | Fraction | Meaning |
|---|---|---|
| all 0s | 0 | ±0 |
| all 0s | non-zero | subnormal |
| all 1s | 0 | ±infinity |
| all 1s | non-zero | NaN |

So a float's normal exponent range is 1 to 254 (true exponent −126 to +127). The largest finite value has the biggest normal exponent and every fraction bit set:

```formula
v_max = (2 − 2^{−m}) × 2^{E_max}
(2 − 2^{−23}) × 2^127 ≈ 3.40 × 10^38
(2 − 2^{−52}) × 2^1023 ≈ 1.80 × 10^308
where
v_max: the largest finite value the format can hold
m: the number of stored fraction bits (23 for float, 52 for double)
2 − 2^{−m}: the significand 1.111...1 in binary with m ones after the point, just under 2
E_max: the largest true exponent of a normal number, equal to the bias (127 for float, 1023 for double)
≈: approximately equal to (rounded)
In words: just under 2, times 2 to the largest exponent, is the largest float; anything bigger overflows to infinity under the default rounding.
```

### Signed zero

+0 (`0x00000000`) and −0 (`0x80000000`) compare equal, but they are different values. Under IEEE 754 non-trapping arithmetic, `1 / -0.0` is −infinity. C requires an implementation providing the relevant IEC 60559/Annex F behaviour; plain ISO C does not universally promise this result. They record which side of zero a tiny result underflowed from, which matters in complex arithmetic and some physics code.

### Infinity

Under the usual non-trapping round-to-nearest mode, overflow produces ±infinity rather than integer-style wrapping; directed rounding modes may instead return a largest finite value. For example, `1e308 * 10` is `inf`. IEEE 754 non-trapping division gives +infinity for `1.0 / 0.0`; C implementations following Annex F provide that behaviour. Python instead raises `ZeroDivisionError`. Integer division by zero in C is undefined. Infinity behaves sensibly: `inf + 1 == inf`, `1 / inf == 0`.

### NaN

**NaN** (not a number) is the result of invalid operations: `0.0 / 0.0`, `inf - inf`, `sqrt(-1.0)`. NaN propagates through ordinary operations such as addition and multiplication, often contaminating a calculation. Some functions have specified exceptions: Python `math.pow(float("nan"), 0.0)` returns 1.0. Python also raises exceptions for operations such as `0.0 / 0.0` and `math.sqrt(-1.0)` instead of returning NaN.

NaN is **unequal to everything, including itself**. for ordinary floating-point values, `x != x` is true only for NaN, which is the traditional test. Use `math.isnan(x)` in Python and `isnan(x)` in C. NaNs do not supply an ordinary total numeric ordering, so a sort using plain numeric comparisons may not give the ordering you intended. Choose explicitly where NaNs should go.

### Subnormals

Without special handling, the smallest positive float would be 1.0 × 2^−126 ≈ 1.18 × 10^−38, and there would be a gap down to 0. **Subnormal** (denormal) numbers fill it. With exponent field 0, the hidden bit becomes 0 and the exponent is fixed at −126:

```formula
v = (−1)^s × 0.f × 2^{−126}
v_min = 2^{−23} × 2^{−126} = 2^{−149}
2^{−149} ≈ 1.4 × 10^{−45}
where
v: the value of a subnormal float
s: the sign bit
0.f: the significand with a leading 0 instead of the hidden 1, then the 23 stored fraction bits f
f: the fraction field
v_min: the smallest positive subnormal float: only the last fraction bit set
2^{−23}: the weight of the last fraction bit
2^{−126}: the fixed scale for subnormal floats, the same as the smallest normal exponent
≈: approximately equal to
In words: subnormals give up the hidden 1 to keep counting down in equal steps, reaching about 1.4 × 10^−45 before zero.
```

So values shrink smoothly down to 2^−149 instead of jumping straight from 2^−126 to 0.

With gradual underflow and correctly rounded subtraction of finite inputs in the same format, distinct representable numbers do not collapse to zero merely because their difference is tiny. Some processors and operations incur costly assists for subnormal operands or results; others handle them efficiently. FTZ and DAZ modes change arithmetic semantics by flushing small results or treating small inputs as zero, so enable them only when the application tolerates that change.

## Real-world failures and fixes

> [!example] The Patriot missile, 1991
> The GAO investigation found that limited precision in a time conversion caused an increasingly inaccurate tracking calculation. After over 100 hours of continuous operation, the system looked in the wrong place for the incoming Scud, which hit barracks and killed 28 Americans. This was an accumulated numerical conversion error, not physical clock drift or a failure of IEEE binary32 specifically. The GAO reports a roughly 0.34-second time error at 100 hours.


Practical rules:

- **Choose equality semantics for the problem.** Exact equality is appropriate for some exact/discrete computations. For approximate results use justified relative and absolute tolerances; near zero, a positive abs_tol may be needed. `math.isclose` does not choose a scientifically valid error allowance for you.
- **Do not store money in floats.** Use integer minor units (pence, cents) or a decimal type such as Python's `decimal.Decimal` or SQL's `NUMERIC`.
- **Order of operations matters.** Float addition is not associative: `(0.1 + 0.2) + 0.3` is 0.6000000000000001, but `0.1 + (0.2 + 0.3)` is 0.6. Parallel reductions on GPUs can give slightly different answers from run to run for this reason.
- **Summing many values** can accumulate rounding error. Compensated summation and math.fsum reduce it; they do not make every result exact or eliminate all overflow and platform effects. Since Python 3.12, the built-in `sum()` also uses compensated summation for floats, so `sum([0.1] * 10)` is 1.0, while a plain `+=` loop gives 0.9999999999999999.
- **Avoid subtracting nearly equal numbers** when you can rearrange the formula. Cancellation can expose error already present in approximate operands and produce a large relative error. Subtraction of nearby floating-point values can itself be exact; rearrangement is useful when it improves the conditioning or avoids prior errors.

## Smaller floats for machine learning

Many neural-network workloads can use reduced precision with suitable training and accumulation strategies. Halving element size halves storage for the same tensor, not necessarily total model memory or traffic: auxiliary states and wider accumulators remain. Two common 16-bit formats are:

| Format | Sign/Exp/Frac | Max |
|---|---|---|
| FP16 (half) | 1 / 5 / 10 | 65,504 |
| bfloat16 | 1 / 8 / 7 | ≈ 3.39e38 |

The maxima come from the same largest-value formula as for float and double:

```formula
v_max = (2 − 2^{−m}) × 2^{E_max}
(2 − 2^{−10}) × 2^15 = 65,504
(2 − 2^{−7}) × 2^127 ≈ 3.39 × 10^38
where
v_max: the largest finite value the format can hold
m: the number of stored fraction bits (10 for FP16, 7 for bfloat16)
E_max: the largest true exponent of a normal number (15 for FP16, 127 for bfloat16)
2 − 2^{−m}: the largest significand, just under 2
≈: approximately equal to
In words: FP16's 5-bit exponent stops at 2 to the 15, so its largest value is only 65,504; bfloat16 keeps float32's 8-bit exponent and so reaches about 3.4 × 10^38.
```

**bfloat16**, used by Google TPUs, has the same sign and exponent widths as float32 but a shorter fraction. Conversion normally rounds rather than simply discarding bits. Its normal exponent range matches float32, with slightly different finite limits and fewer subnormal values. FP16 has more precision but a maximum of 65,504. Loss scaling helps prevent small gradients from underflowing; it does not fix activations that exceed FP16's maximum. Recent GPUs go further with 8-bit and even 4-bit floating-point formats.

## Key takeaways
- A normal binary interchange value is the sign, times 1.fraction in binary, times 2 to the power (stored exponent minus the bias); subnormals, zeros, infinities and NaNs use special encodings.
- float: 1 + 8 + 23 bits, bias 127, about 7 digits. double: 1 + 11 + 52 bits, bias 1023, about 16 digits.
- To encode: write in binary, normalise, add the bias to the exponent, store the bits after the point.
- With usual binary64 nearest-even evaluation, `0.1 + 0.2 != 0.3`. Use justified tolerances for approximate results; exact equality remains appropriate when exact value comparison is intended.
- The gap between floats grows with magnitude: all integers in the consecutive ranges through 2^24 (binary32) and 2^53 (binary64) are exact, but larger values are representable only at wider spacing.
- Exponent all 1s means infinity or NaN; all 0s means zero or subnormal. NaN is not equal to itself.
- Use integers or decimals for money, and compensated summation for long sums.

## Further reading
- [IEEE 754 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_754)
- [Single-precision floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
- [What Every Computer Scientist Should Know About Floating-Point Arithmetic — David Goldberg](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Floating-point arithmetic: issues and limitations — Python docs](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Float Toy — interactive bit editor](https://evanw.github.io/float-toy/)
- [Bfloat16 floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format)

- [GAO investigation of the Dhahran Patriot failure](https://www.gao.gov/assets/imtec-92-26.pdf)
- [Python math accuracy and isclose](https://docs.python.org/3/library/math.html)
- [Google TPU bfloat16 semantics](https://cloud.google.com/tpu/docs/bfloat16)
