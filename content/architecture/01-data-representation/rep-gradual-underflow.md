---
id: rep-gradual-underflow
title: Subnormals and gradual underflow
level: intermediate
minutes: 3
summary: A zero hidden bit extends the range towards zero with fixed spacing.
sourceLesson: rep-floating-point
---

This unit continues the preceding material on binary floating-point representations.

### Subnormals

Without special handling, the smallest positive float would be 1.0 × 2^−126 ≈ 1.18 × 10^−38, and there would be a gap down to 0. **Subnormal** (denormal) numbers fill it. With exponent field 0, the hidden bit becomes 0 and the exponent is fixed at −126:

```formula
v = (−1)^s (0.f) 2^{−126}
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

## Key takeaways
- A zero hidden bit extends the range towards zero with fixed spacing.
- Flush-to-zero modes change numerical results.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
