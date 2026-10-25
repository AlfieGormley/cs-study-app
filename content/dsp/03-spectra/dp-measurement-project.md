---
id: dp-measurement-project
title: A reproducible vibration measurement
level: intermediate
minutes: 5
summary: Combine known timing, RMS, causal filtering and a calibrated spectrum with explicit synthetic checks.
---

Build a small synthetic vibration experiment before trusting a real measurement chain. The input contains a fixed acceleration offset, a wanted 64 Hz tone and a 192 Hz interferer. Its values are in metres per second squared. We know the truth because we generated the record; a physical sensor would add calibration uncertainty, noise, drift and timing error.

The aim is to preserve the wanted tone, reduce the interferer and check that the measured output matches the chosen filter. These are calculations on a host computer, not a device benchmark or evidence that a sensor is accurate.

## State the experiment's contract

Use 1024 samples per second and acquire 1280 samples. Remove the measured mean, apply a causal three-tap moving average with zero initial state, then discard the first 256 outputs and analyse the next 1024. This removes the filter's startup from the analysed segment. The remaining tones complete whole cycles in that segment.

The symmetric three-tap filter has one input-sample delay. Keep that delay when interpreting time events. We estimate amplitudes here, not aligned transient times, and do not substitute an offline zero-phase filter.

## Complete Python experiment

`lfilter` applies the stated coefficients causally and starts with zero state when no initial state is supplied. `mean` and `sqrt(mean(...))` calculate the offset and RMS. `allclose` checks approximate equality with an explicit absolute tolerance. No random noise or external files are involved.

```python
import numpy as np
from scipy.signal import lfilter
from scipy.signal.windows import hann

fs = 1024
n = np.arange(1280)
x = 0.4 + 2 * np.cos(
    2 * np.pi * 64 * n / fs)
x += 0.6 * np.cos(
    2 * np.pi * 192 * n / fs)
offset = x.mean()
ac = x - offset
h = np.ones(3) / 3
y = lfilter(h, [1.0], ac)
v = y[256:1280]
w = hann(len(v), sym=False)
A = abs(np.fft.rfft(v * w)) / w.sum()
A[1:-1] *= 2
print(round(offset, 6))
print(round(np.sqrt(np.mean(ac**2)), 6))
print(np.round(A[[64, 192]], 6))
# Direct sinusoidal filter gains.
freq = np.array([64, 192])
gain = abs((1 + 2 * np.cos(
    2 * np.pi * freq / fs)) / 3)
expect = np.array([2.0, 0.6]) * gain
assert np.allclose(A[[64, 192]], expect,
                   atol=1e-10, rtol=0)
```

The outputs are `0.4`, `1.476482` and `[1.898506 0.353073]`. Acceleration amplitudes and RMS share the input unit. The interferer is reduced, not eliminated. The wanted tone is also attenuated, so reading its output peak as its original input amplitude would be wrong.

## Explain the expected values

For this three-tap moving average, the steady sinusoidal magnitude gain follows from adding the three delayed complex contributions. Its magnitude is dimensionless.

```formula
G(f) = |1 + 2 cos((2πf) / F_s)| / 3
A_o = A_i G(f)
where
G: magnitude gain function of this specific equal-weight three-tap moving average
f: sinusoid frequency, in hertz (Hz)
cos: cosine function with an angle in radians
π: pi, approximately 3.14159
F_s: sample rate, here 1024 Hz
| |: absolute value of the real expression between the bars
A_o: steady output peak amplitude, in metres per second squared
A_i: input peak amplitude of the same sinusoid, in metres per second squared
Hz: hertz, cycles per second
In words: multiply each input tone's peak by the filter's gain at that frequency to predict its steady output peak.
```

This formula checks magnitude only. The causal filter also changes phase. The analyser uses a periodic Hann and corrects coherent gain using its actual sum; the analysed frequencies are interior bins, well away from both endpoints.

The input's AC RMS can also be predicted because the two cosines have zero mean and are orthogonal over the complete record: their cross-products sum to zero.

```formula
R = √((a^2 + b^2) / 2)
R = √(((2 u)^2 + (0.6 u)^2) / 2)
R ≈ 1.476482 u
where
R: RMS of this zero-mean two-tone input over whole cycles, in acceleration units u
a: wanted tone's peak amplitude, here 2 u
b: interferer's peak amplitude, here 0.6 u
u: acceleration unit, one metre per second squared
√: non-negative square-root function
≈: approximately equal to, after rounding
In words: the mean-square contributions of these orthogonal whole-cycle tones add before taking the square root.
```

## What the checks establish

The assertion checks this implementation against a separate analytical gain expression. Also check timing, offset and units; one passing spectrum assertion cannot prove every part of a measurement system. A longer filter could better suppress the interferer, at a cost in delay and transition behaviour.

On a real signal, record the sample-clock accuracy, calibration, detrending, window, bandwidth and transient policy. A peak's bin label alone does not supply an uncertainty interval.

## Key takeaways

- A reproducible synthetic signal supplies known truth for checking a DSP chain.
- Predict the filter's effect before interpreting the measured output spectrum.
- Numerical agreement does not establish physical calibration, timing accuracy or real-time performance.

## Further reading

- [SciPy: causal filtering and initial conditions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
- [SciPy: periodic and symmetric Hann windows](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hann.html)
- [NumPy: FFT conventions](https://numpy.org/doc/stable/reference/routines.fft.html)
