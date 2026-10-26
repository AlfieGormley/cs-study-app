---
id: rep-float-special-values
title: Zeros, infinities and NaNs
level: intermediate
minutes: 3
summary: Reserved exponent fields encode zeros, subnormals, infinities and NaNs.
sourceLesson: rep-floating-point
---

Some floating-point bit patterns represent exceptional states instead of ordinary finite magnitudes. Classifying these states helps diagnose failed calculations.

## Special values

The all-zeros and all-ones exponents are reserved:

| Exponent | Fraction | Meaning |
|---|---|---|
| all 0s | 0 | ±0 |
| all 0s | non-zero | subnormal |
| all 1s | 0 | ±infinity |
| all 1s | non-zero | NaN |

So a float's normal exponent range is 1 to 254 (true exponent −126 to +127). The largest finite value has the biggest normal exponent and every fraction bit set:

The largest finite binary32 value is about 3.40 × 10^38, and binary64 reaches about 1.80 × 10^308. A mathematical result just above the maximum can still round back to it; a sufficiently large result rounds to infinity in nearest-even mode.

### Signed zero

+0 (`0x00000000`) and −0 (`0x80000000`) compare equal, but they have different encodings and retain different signs. Under IEEE 754 non-trapping arithmetic, `1 / -0.0` is −infinity. C requires an implementation providing the relevant IEC 60559/Annex F behaviour; plain ISO C does not universally promise this result. They record which side of zero a tiny result underflowed from, which matters in complex arithmetic and some physics code.

### Infinity

Under the usual non-trapping round-to-nearest mode, overflow produces ±infinity rather than integer-style wrapping; directed rounding modes may instead return a largest finite value. For example, `1e308 * 10` is `inf`. IEEE 754 non-trapping division gives +infinity for `1.0 / 0.0`; C implementations following Annex F provide that behaviour. Python instead raises `ZeroDivisionError`. Integer division by zero in C is undefined. Infinity behaves sensibly: `inf + 1 == inf`, `1 / inf == 0`.

### NaN

**NaN** (not a number) is the result of invalid operations: `0.0 / 0.0`, `inf - inf`, `sqrt(-1.0)`. NaN propagates through ordinary operations such as addition and multiplication, often contaminating a calculation. Some functions have specified exceptions: Python `math.pow(float("nan"), 0.0)` returns 1.0. Python also raises exceptions for operations such as `0.0 / 0.0` and `math.sqrt(-1.0)` instead of returning NaN.

NaN is **unequal to everything, including itself**. for ordinary floating-point values, `x != x` is true only for NaN, which is the traditional test. Use `math.isnan(x)` in Python and `isnan(x)` in C. NaNs do not supply an ordinary total numeric ordering, so a sort using plain numeric comparisons may not give the ordering you intended. Choose explicitly where NaNs should go.

## Key takeaways
- Reserved exponent fields encode zeros, subnormals, infinities and NaNs.
- Language error handling can differ from non-trapping IEEE arithmetic.
- NaN compares unequal to itself.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
