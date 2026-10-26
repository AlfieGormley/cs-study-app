---
id: df-stability-precision
title: Stability and numerical limits
level: intermediate
minutes: 4
summary: Separate bounded-output mathematics from overflow, coefficient rounding and finite test evidence.
---

**Bounded-input bounded-output stability**, or **BIBO stability**, means every bounded input produces a bounded output for the stated system and initial conditions. “Bounded” means there is a finite ceiling on absolute magnitude for all time; it does not mean “small enough for this particular computer type”. Here we analyse causal filters in zero state with exact arithmetic first.

## Why the convex smoother stays bounded

The previous lesson's smoother uses positive weights that add to one. If the new reading and previous output both lie within a fixed magnitude bound, their weighted average stays inside it too. It cannot exceed both values or fall below both. Zero initial output starts inside the bound, so the same reasoning applies at the first update, the second and every later update.

This proves a useful property for this specific normalised smoother. Negative feedback coefficients require a different magnitude argument. A fixed FIR with finitely many finite coefficients is also BIBO stable: each output adds only a fixed finite number of bounded contributions.

## A one-pole condition, with its scope

Now consider a different rule: add the whole current input to a fixed multiple of the previous output. Here the input weight stays one; it is not reduced to complement the memory weight. Its **filter pole** is the memory multiplier: an existing disturbance is repeatedly multiplied by it.

If the multiplier's magnitude is below one, old contributions shrink fast enough for every bounded input to give a bounded output. A negative multiplier can be stable too: its sign alternates the old contribution while its magnitude shrinks. This condition belongs to this specific one-pole rule; more complicated recursive filters need their own analysis.

The optional reference records the rule and its strict stability boundary.

```formula reference
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

At a multiplier of one, constant positive input accumulates without limit. At minus one, an alternating bounded input can likewise make the output's magnitude grow. Beyond either boundary, even a single impulse leaves a growing response. A finite test that happens to look quiet cannot prove stability for every bounded input: the choice of test signal and how long you observe it both matter.

## The computer is a separate constraint

**Numerical overflow** occurs when a result exceeds a representation's range. A stable filter with gain 100 can still overflow a narrow integer type when a large bounded input arrives. **Rounding error** occurs because many values have no exact finite representation. Rounding coefficients can also change the implemented filter, so check its actual stored coefficients, especially near a stability boundary.

For example, doubling is a stable mathematical operation: any finite input bound gives a finite output bound. A narrow integer representation can still fail to hold the doubled value. Depending on the arithmetic rules, overflow may wrap to an unexpected value, saturate at a limit or raise an error. None of those outcomes turns the exact mathematical gain into an unstable system; they show that the implementation needs a separate range check.

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
