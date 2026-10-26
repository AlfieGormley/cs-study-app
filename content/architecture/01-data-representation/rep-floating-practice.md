---
id: rep-floating-practice
title: Numerical safeguards and smaller floats
level: intermediate
minutes: 3
summary: Use tolerances justified by the application and exact decimal or integer money values.
sourceLesson: rep-floating-point
---

Choose a numeric representation and error policy for the application. More bits help only when they address the actual failure: range, precision or an exactness requirement.

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

The exponent controls the broad range while fraction bits control precision. A wider exponent can keep large activations finite, but fewer fraction bits mean coarser rounding.

**bfloat16**, used by Google TPUs, has the same sign and exponent widths as float32 but a shorter fraction. Conversion normally rounds rather than simply discarding bits. Its normal exponent range matches float32, with slightly different finite limits. Subnormal handling depends on the implementation: Cloud TPU conversion flushes bfloat16 subnormals to zero. FP16 has more precision but a maximum of 65,504. Loss scaling helps prevent small gradients from underflowing; it does not fix activations that exceed FP16's maximum. Recent GPUs go further with 8-bit and even 4-bit floating-point formats.

## Key takeaways
- Use tolerances justified by the application and exact decimal or integer money values.
- Summation order can affect rounded results.
- FP16 and bfloat16 trade precision and exponent range differently.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
- [IEEE 754 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_754)
- [Single-precision floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
- [What Every Computer Scientist Should Know About Floating-Point Arithmetic — David Goldberg](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Floating-point arithmetic: issues and limitations — Python docs](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Float Toy — interactive bit editor](https://evanw.github.io/float-toy/)
- [Bfloat16 floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format)

- [GAO investigation of the Dhahran Patriot failure](https://www.gao.gov/assets/imtec-92-26.pdf)
- [Python math accuracy and isclose](https://docs.python.org/3/library/math.html)
- [Google TPU bfloat16 semantics](https://cloud.google.com/tpu/docs/bfloat16)
