---
id: df-frequency-response
title: What happens to each frequency?
level: intermediate
minutes: 4
summary: Interpret steady-state gain and phase, and turn a vague smoothing goal into frequency requirements.
---

A filter can preserve a slowly varying trend while reducing faster oscillations. Its **frequency response** describes how a stable LTI system scales and shifts sinusoids at each frequency after startup effects have passed. **Amplitude response** gives the amplitude ratio; **phase response** gives the phase shift. A negative output value at one instant is not a negative amplitude ratio: amplitude ratios are nonnegative.

For a sinusoid present long enough for steady behaviour and a nonzero output amplitude, the following description applies. It uses radians for phase and hertz for frequency. At a response zero the output is zero and its phase is undefined; exclude that case from the phase-bearing expression below.

```formula
x[n] = A cos(2πfn / F_s + φ)
y[n] = AG cos(2πfn / F_s + φ + θ)
where
x: the sinusoidal input sequence, with dimensionless sample values
y: the steady-state output sequence, in the same dimensionless units
n: the integer sample index of the ideal continuing steady-state sinusoid
A: the positive input peak amplitude, dimensionless here
G: the positive amplitude gain at the chosen frequency, dimensionless; the zero-gain case is excluded from this expression
f: the sinusoid frequency in hertz (Hz), below half the sample rate
F_s: the sample rate in samples per second
φ: the input phase in radians
θ: the filter's phase shift at this frequency, in radians
π: pi, approximately 3.14159
cos: the cosine function, taking an angle in radians
Hz: hertz, cycles per second
In words: an LTI filter keeps a steady sinusoid's frequency while changing its amplitude and phase.
```

## Measure a simple response

A two-sample moving average has gain 1 for constant input. At a quarter of the sample rate, its gain is about 0.707 and its phase shift is minus a quarter of pi radians. At half the sample rate, alternating 1 and minus 1 cancel exactly once the history is filled. These different outcomes are the same filter acting on different frequencies.

The complete example checks the quarter-rate tone after startup. Here `arange` creates integer sample indices and `cos` acts on every array element. The direct expression for the expected output uses the predicted amplitude and half-sample delay. `allclose` compares arrays allowing small floating-point rounding errors.

```python
import numpy as np

n = np.arange(12)
x = np.cos(np.pi*n/2)
y = np.convolve(x, [0.5, 0.5])
expected = np.cos(np.pi*(n-0.5)/2)
expected *= np.sqrt(0.5)
assert np.allclose(y[1:12], expected[1:])
```

## Specify useful and unwanted bands

The **passband** is the frequency region intended to pass within a specified gain tolerance. The **stopband** is intended to be sufficiently reduced. The **transition band** lies between them. A **low-pass filter** passes low frequencies and reduces higher ones, but no finite filter here makes an instantaneous jump between perfect passage and perfect rejection.

For a 100-sample-per-second sensor, an illustrative requirement might preserve 0–2 Hz within a chosen tolerance and strongly reduce frequencies above 15 Hz. The tolerated gain error and required reduction must also be stated before deciding whether a design succeeds.

A moving average has cancellation frequencies but also unwanted lobes between them. Increasing its length does not turn it into a universal frequency separator. It also cannot recover information already lost to aliasing, and it reduces useful signal components occupying the same frequencies as unwanted noise. Define the task before choosing the filter.

## Key takeaways
- Stable LTI filtering changes steady-state sinusoidal amplitude and phase, not frequency.
- Startup behaviour must be excluded or modelled when measuring response.
- Passband, stopband, tolerances and timing requirements guide filter choice.

## Further reading
- [Julius O. Smith: frequency response](https://www.dsprelated.com/freebooks/filters/Frequency_Response.html)
- [Julius O. Smith: steady sinusoidal response](https://www.dsprelated.com/freebooks/filters/Introduction_I_I.html)
- [Smith: moving average frequency behaviour, Chapter 15](https://www.dspguide.com/CH15.PDF)
