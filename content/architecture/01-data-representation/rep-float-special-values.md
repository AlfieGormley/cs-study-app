---
id: rep-float-special-values
title: Zeros, infinities and NaNs
level: intermediate
minutes: 3
summary: Reserved exponent fields encode zeros, subnormals, infinities and NaNs.
sourceLesson: rep-floating-point
---

This unit continues the preceding material on binary floating-point representations.

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
v_max = (2 − 2^{−m}) 2^{E_max}
(2 − 2^{−23}) × 2^127 ≈ 3.40 × 10^38
(2 − 2^{−52}) × 2^1023 ≈ 1.80 × 10^308
where
v_max: the largest finite value the format can hold
m: the number of stored fraction bits (23 for float, 52 for double)
2 − 2^{−m}: the significand 1.111...1 in binary with m ones after the point, just under 2
E_max: the largest true exponent of a normal number, equal to the bias (127 for float, 1023 for double)
≈: approximately equal to (rounded)
In words: just under two, times two to the largest exponent, is the largest finite value. A mathematical result just above it can still round back to it; a sufficiently large result rounds to infinity in nearest-even mode.
```

### Signed zero

+0 (`0x00000000`) and −0 (`0x80000000`) compare equal, but they are different values. Under IEEE 754 non-trapping arithmetic, `1 / -0.0` is −infinity. C requires an implementation providing the relevant IEC 60559/Annex F behaviour; plain ISO C does not universally promise this result. They record which side of zero a tiny result underflowed from, which matters in complex arithmetic and some physics code.

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
