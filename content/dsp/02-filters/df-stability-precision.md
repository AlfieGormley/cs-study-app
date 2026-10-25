---
id: df-stability-precision
title: Stability and numerical limits
level: intermediate
minutes: 5
summary: Separate bounded-output mathematics from overflow, coefficient rounding and finite test evidence.
---

**Bounded-input bounded-output stability**, or **BIBO stability**, means every bounded input produces a bounded output for the stated system and initial conditions. “Bounded” means there is a finite ceiling on absolute magnitude for all time; it does not mean “small enough for this particular computer type”. Here we analyse causal filters in zero state with exact arithmetic first.

## Why the convex smoother stays bounded

The previous lesson's smoother uses positive weights that add to one. If the new reading and previous output both lie within a fixed magnitude bound, their weighted average stays inside it too.

```formula
y[n] = (1 − a)x[n] + ay[n − 1]
0 ≤ a < 1
|x[n]| ≤ B
|y[n − 1]| ≤ B
|y[n]| ≤ (1 − a)B + aB = B
where
y: the output sequence, with dimensionless sample values; zero initial state satisfies the bound
x: the input sequence, with dimensionless sample values
n: the integer sample index, starting at zero; the previous output before the record is zero
a: the dimensionless previous-output weight in the stated range
B: a finite nonnegative magnitude bound, in the same dimensionless units as the samples
| |: absolute value, the nonnegative magnitude of a real number
≤: less than or equal to
In words: a weighted average of two readings inside the bound stays inside the bound, so the argument continues sample after sample.
```

This proves a useful property for this specific normalised smoother. Negative feedback coefficients require a different magnitude argument. A fixed FIR with finitely many finite coefficients is also BIBO stable: each output adds only a fixed finite number of bounded contributions.

## A one-pole condition, with its scope

For the following different recurrence, the input weight is fixed at 1. Its **filter pole** is the memory multiplier: an existing disturbance is repeatedly multiplied by it. This beginner example avoids needing a general pole-zero calculation.

```formula
y[n] = x[n] + py[n − 1]
|p| < 1
where
y: the causal output sequence in zero initial state, with dimensionless samples
x: the input sequence, with dimensionless samples and input weight fixed at one
n: the integer sample index, starting at zero; the previous output before the record is zero
p: the real dimensionless memory multiplier and the pole of this specific recurrence
| |: absolute value, ignoring the sign of the real multiplier
<: strictly less than
In words: this one-pole filter is BIBO stable exactly when the magnitude of its memory multiplier is below one.
```

With a multiplier of 0.5, an impulse produces 1, 0.5, 0.25 and progressively smaller values. With 1, a constant input of 1 produces 1, 2, 3 and unbounded growth. With minus 1, an alternating bounded input can likewise make the magnitude grow. A finite test that happens to look quiet cannot prove stability for every bounded input.

## The computer is a separate constraint

**Numerical overflow** occurs when a result exceeds a representation's range. A stable filter with gain 100 can still overflow a narrow integer type when a large bounded input arrives. **Rounding error** occurs because many values have no exact finite representation. Rounding coefficients can also change the implemented filter, so check its actual stored coefficients, especially near a stability boundary.

This complete example deliberately uses signed 16-bit integer array arithmetic. It shows overflow in a simple gain operation, not a complete fixed-point filter implementation.

```python
import numpy as np

x = np.array([20000], dtype=np.int16)
y = x * np.int16(2)
print(y.tolist())
# [-25536]
```

Use suitable types, scaling, numerical range validation and representative stress inputs. Floating-point arithmetic also has finite precision and range. SciPy recommends second-order-section filtering for most general IIR tasks because it reduces numerical problems; our one-state example does not establish safety for high-order direct forms.

## Key takeaways
- Mathematical stability concerns all bounded inputs over unlimited time.
- The stated one-pole condition belongs to a specific nondegenerate recurrence.
- Stable mathematics does not eliminate representation limits or implementation errors.

## Further reading
- [MIT: convolution models and BIBO stability](https://web.mit.edu/6.02/www/s2012/handouts/11.pdf)
- [Julius O. Smith: one-pole stability](https://www.dsprelated.com/freebooks/filters/One_Pole.html)
- [NumPy: numerical scalar types and overflow](https://numpy.org/doc/stable/reference/arrays.scalars.html)
- [SciPy: filtering and numerical recommendations](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
