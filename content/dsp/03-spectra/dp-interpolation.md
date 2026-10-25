---
id: dp-interpolation
title: Increase sample rate with interpolation
level: intermediate
minutes: 5
summary: Follow zero insertion, spectral images and the low-pass gain needed to reconstruct between samples.
---

**Interpolation** estimates samples at new time positions from an existing sampled signal. It does not recover frequencies already lost to aliasing. Integer-rate interpolation can be understood as inserting zeros between samples and then applying a reconstruction low-pass filter.

The inserted zeros are placeholders, not claims that the physical signal was zero at those instants. Interpreting the longer sequence at the increased rate preserves the original sample times.

## Insert first, filter second

For a factor of two, the sequence `[1, 1, 1]` becomes `[1, 0, 1, 0, 1, 0]` if we allocate six output positions. An efficient implementation may avoid calculating the explicit zeros, but this model explains the operation.

```formula
F_o = L F_i
F_o = 2 × 100 Hz = 200 Hz
where
F_o: output sample rate, in hertz (Hz)
L: positive integer interpolation factor, here 2
F_i: original sample rate, here 100 Hz
Hz: hertz, cycles per second
In words: doubling the number of time positions per original interval doubles the sample rate, while the original values keep their original times.
```

Zero insertion produces **spectral images**: repeated copies of the original baseband spectrum in the enlarged frequency range. A reconstruction low-pass filter suppresses those images while retaining the wanted band. Unlike decimation aliasing, the separated images can be removed before they are folded onto the baseband.

For a constant input, the zero-inserted sequence's average is reduced by the insertion factor. A unity-gain low-pass would retain that reduced average. The interpolation filter therefore needs DC gain equal to the insertion factor, when the zeros are inserted explicitly without another scale correction. Its passband should have the corresponding gain where faithful reconstruction is required.

## A transparent toy interpolator

The three coefficients below implement linear interpolation for a factor of two. Their sum is two. The causal full convolution includes one high-rate-sample delay and edge transients. It is a teaching example: its frequency response is too gradual for demanding image suppression.

```python
import numpy as np

x = np.ones(3)
z = np.zeros(2 * len(x))
z[::2] = x
h = np.array([0.5, 1.0, 0.5])
y = np.convolve(z, h, mode="full")
print(z.tolist())
print(y.tolist())
# The interior returns to the constant 1.
```

The outputs are `[1.0, 0.0, 1.0, 0.0, 1.0, 0.0]` and `[0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0]`. The explicitly allocated zero at the end explains the final zero. Different full-output length policies can omit that unnecessary last position.

> [!analogy] Real-world analogy: filling a timetable
> Put the known appointments into a timetable with twice as many time slots. Empty slots reserve positions; they do not mean the activity stopped.
>
> **How it maps:** Original samples retain their timing while zero placeholders create new positions. The filter estimates values at and around those positions.
>
> **Where it stops:** Signal interpolation depends on a bandwidth assumption and a numerical filter, not judgement about appointments. It cannot invent unknown high-frequency information.

## Rational rate conversion

**Resampling** can increase by one integer factor and decrease by another. SciPy's `resample_poly` combines zero insertion, low-pass FIR filtering and reduction efficiently using **polyphase** computation. It supplies the required internal scaling; do not manually multiply its default output by the insertion factor again.

Its default boundaries assume zeros beyond the finite input, and its filter alignment differs from a causal full-convolution stream. Inspect edges and timing before comparing results. A filter for the intermediate increased rate must satisfy both image suppression and the final output's anti-alias requirements.

## Key takeaways

- Zero insertion creates positions and spectral images; low-pass filtering produces the interpolated signal.
- An explicitly zero-inserted interpolator needs the appropriate gain, not just image rejection.
- A library's scaling, boundary extension and time alignment are part of its contract.

## Further reading

- [SciPy: upsample, FIR filter and downsample](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.upfirdn.html)
- [SciPy: polyphase resampling](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html)
