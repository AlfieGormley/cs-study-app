---
id: dp-downsampling
title: Reduce sample rate without folding signals
level: intermediate
minutes: 5
summary: Set a new Nyquist limit, low-pass first and understand why keeping every second sample is insufficient.
---

Keeping every second or third sample is simple. Keeping the meaning of those samples takes more care. **Decimation** combines low-pass filtering with retaining samples at a lower rate. Frequencies that were safe at the original rate can exceed the new Nyquist limit and alias into the wanted band.

## Design for the new rate first

For an integer reduction factor, both the output sample rate and its Nyquist limit decrease.

```formula
F_o = F_i / D
f_N = F_o / 2
F_o = 1200 Hz / 3 = 400 Hz
f_N = 400 Hz / 2 = 200 Hz
where
F_o: output sample rate, in hertz (Hz)
F_i: input sample rate, here 1200 Hz
D: positive integer decimation factor, here 3
f_N: output Nyquist frequency, in Hz
Hz: hertz, cycles per second
In words: keeping every third sample reduces a 1200-sample-per-second record to 400 samples per second, so the new Nyquist boundary is 200 hertz.
```

Wanted baseband content must lie strictly below the new Nyquist frequency. A practical low-pass filter also needs a transition band: do not place the wanted passband edge exactly at Nyquist and expect an instantaneous cut-off. Choose stopband attenuation from how much aliased interference the application can tolerate.

Filtering after retaining samples cannot generally undo aliasing. Different original frequencies have already become indistinguishable. This digital prefilter protects a later digital rate reduction; it cannot repair aliasing that already happened at the original analogue-to-digital conversion.

> [!analogy] Real-world analogy: checking before a narrow doorway
> Remove oversized items before sending a mixed delivery through a narrow doorway. Sorting afterwards cannot recover information lost when items were forced together.
>
> **How it maps:** The new rate has a smaller unambiguous frequency range. The prefilter suppresses components outside it before samples are discarded.
>
> **Where it stops:** Aliasing is an exact ambiguity between sampled oscillations, not physical damage or a queue. A real filter only attenuates unwanted components by a finite amount.

## Complete Python example

A 350 Hz cosine sampled at 1200 Hz is initially below Nyquist. Retaining every third sample without filtering gives a 50 Hz alias at the 400 Hz output rate. `resample_poly(x, 1, 3)` instead applies a low-pass FIR filter before reduction. Its documented zero-phase alignment is an offline boundary-handling choice; it is not the delayed output of a causal streaming filter.

```python
import numpy as np
from scipy.signal import resample_poly

fs = 1200
n = np.arange(1200)
x = np.cos(2 * np.pi * 350 * n / fs)
bad = x[::3]
good = resample_poly(x, 1, 3)
f = np.fft.rfftfreq(len(bad), 1 / 400)
print(f[np.argmax(abs(np.fft.rfft(bad)))])
# Exclude edges of the finite FIR result.
print(round(np.sqrt(np.mean(bad**2)), 3))
print(np.sqrt(np.mean(good[40:-40]**2))
      < 0.002)
```

The outputs are `50.0`, `0.707` and `True`. The final check is specific to this synthetic signal, filter and interior segment. It is not a guaranteed stopband specification for every rate or input. Production work needs a filter specification, transient policy and tests across the unwanted band.

## Key takeaways

- Work out the output rate and Nyquist boundary before discarding samples.
- Low-pass before decimation, leaving room for a real filter's transition band.
- Record causal delay or offline alignment and boundary assumptions explicitly.

## Further reading

- [SciPy: decimation includes an anti-alias filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.decimate.html)
- [SciPy: polyphase resampling and boundary assumptions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html)
