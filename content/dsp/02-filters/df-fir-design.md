---
id: df-fir-design
title: Design and inspect a small FIR filter
level: intermediate
minutes: 5
summary: Design a low-pass FIR, check its actual response, and account for symmetric-filter delay.
---

A **finite impulse response**, or **FIR**, filter has an impulse response that becomes exactly zero after a finite number of samples. A direct FIR implementation multiplies present and past inputs by fixed **filter coefficients** and adds them. Each coefficient is often called an **FIR tap**. A moving average is an FIR with equal taps; useful FIR filters need not use equal or positive coefficients.

## Ask a design tool a precise question

SciPy's `signal.firwin` designs FIR coefficients using the **window method**: it limits and shapes an ideal response's coefficient sequence. The details of window choices come later. Here we request 31 taps, a Hamming window, a low-pass response, and an explicit sample rate of 100 samples per second.

The `cutoff` of 10 Hz is this API's half-amplitude point, approximately minus 6 dB, rather than a promise that every frequency below 10 Hz has gain 1. `scale=True` normalises this low-pass design to unity gain at DC. Always check an API's convention before treating a parameter as a passband edge.

This complete example measures the returned coefficients using `freqz`. Its frequency argument is a one-dimensional array of frequencies in hertz because `fs` is supplied. `abs` obtains the magnitude of the complex response; `round` only formats the printed values.

```python
import numpy as np
from scipy import signal

b = signal.firwin(
    31, 10, fs=100, window="hamming",
    pass_zero="lowpass", scale=True)
f = np.array([0.0, 5.0, 10.0, 25.0])
_, response = signal.freqz(b, worN=f,
                         fs=100)
print(np.round(abs(response), 6).tolist())
# [1.0, 0.989021, 0.498204, 5e-06]
assert np.allclose(b, b[::-1])
```

The last displayed value means five millionths after rounding, rather than an exact zero. These are four response checks, not proof that an entire band meets a tolerance. A real specification needs a sufficiently thorough frequency-grid check and attention to extrema between grid points. Increasing the tap count with a comparable window usually narrows the transition, while window choice trades transition width against residual **filter ripple** and stopband attenuation. More taps also mean more work and, for this symmetric design, more delay.

## Symmetry gives a specific delay

Real, symmetric FIR coefficients give linear phase. Their **group delay** is constant wherever the response is nonzero and the phase can be followed continuously. The gain may change sign in the corresponding zero-phase response, causing phase jumps; phase is undefined at exact response zeros.

```formula
D = (M − 1) / 2
τ = D / F_s
D = (31 − 1) / 2 = 15
τ = 15 / (100 s^{−1}) = 0.15 s
where
D: the group delay in sample intervals for a causal real symmetric FIR with nonzero response at the frequency considered
M: the number of coefficients, here 31
τ: the corresponding delay in seconds (s)
F_s: the sample rate in sample intervals per second, here 100
s: second, the unit of time; s to the power minus one means per second
In words: the centre of a symmetric 31-tap causal FIR lies 15 sample intervals behind its newest input, giving 0.15 seconds at this sample rate.
```

An even number of symmetric taps gives a half-integer delay in sample intervals, which is valid. Arbitrary FIR coefficients need not have constant group delay. Nor does “FIR” mean “zero delay”. Shifting a saved output backwards can align a recording, but cannot make future samples available to a live system or undo changed amplitudes. Startup and the finite tail still need a policy.

## Key takeaways
- FIR taps describe finite memory; a design parameter needs an API convention.
- Inspect response, including transition and ripple, against actual requirements.
- Real symmetric FIRs have a known group delay where their response is nonzero.

## Further reading
- [SciPy: firwin design and cutoff convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html)
- [SciPy: freqz response evaluation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html)
- [Julius O. Smith: symmetric linear-phase filters](https://www.dsprelated.com/freebooks/filters/Symmetric_Linear_Phase_Filters.html)
