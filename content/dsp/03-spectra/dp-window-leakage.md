---
id: dp-window-leakage
title: Finite records and spectral leakage
level: intermediate
minutes: 5
summary: Choose a named window, understand its trade-offs and correct coherent tone amplitude.
---

A DFT describes a finite record as a repeating pattern. When a tone does not complete a whole number of cycles in that record, the repeated edges may not join smoothly. Its energy spreads across bins: **spectral leakage**. Even a noiseless, single-frequency input can therefore have many non-zero FFT bins.

Taking an unweighted record applies a **rectangular window**. A **spectral window** is a set of weights multiplied into the samples before transforming. Tapering the ends can suppress distant leakage, but broadens the central response. It does not remove the finite observation limit.

> [!analogy] Real-world analogy: a photograph's soft edge
> A hard-edged cut-out draws attention to its boundary. Fading the edge makes that boundary less abrupt, but blurs where it ends.
>
> **How it maps:** A taper reduces abrupt record boundaries and distant spectral leakage, while broadening a tone's central spectral feature.
>
> **Where it stops:** The broadening comes from Fourier mathematics, not optical focus. A window cannot reveal unrecorded samples or guarantee separation of nearby tones.

## Name the Hann convention

For spectral analysis here, use a **periodic Hann window**: SciPy's `hann(N, sym=False)`. Its final stored value need not be zero. The symmetric Hann, `sym=True`, includes both ends of a symmetric taper and is often used in FIR design. Those two finite arrays have different sums.

```formula
w[n] = 0.5 − 0.5 cos((2πn) / N)
C = (Σ w[n]) / N
where
w[n]: unitless periodic Hann weight at sample n
n: integer sample index, from 0 through N − 1
N: number of weights and input samples, here greater than 2
cos: cosine function with an angle in radians
π: pi, approximately 3.14159
C: coherent gain, the mean of the window weights; 0.5 for this periodic Hann
Σ: add w[n] for every integer n from 0 through N − 1
In words: this Hann taper has an average weight of one half, so it reduces a coherent tone's raw FFT magnitude.
```

The **main lobe** is the central spectral feature produced by a windowed tone. **Side lobes** are its smaller surrounding features. Compared with a rectangular window, Hann has a wider main lobe and lower nearby side lobes. A weak distant tone may become easier to see, while two close tones may become harder to separate. Choice depends on the measurement.

## Correct a coherent tone, with limits

For an isolated interior, bin-centred real sinusoid, divide by the sum of weights rather than by the number of samples. This is exact when the mirrored negative-frequency tone contributes zero at the measured positive bin, and approximate when that contribution is negligible. Check this condition near DC and Nyquist or when changing window conventions. For an off-bin tone this correction alone does not remove peak-bin underestimation, called **scalloping loss**.

```formula
A_k = (2|X_w[k]|) / (Σ w[n])
where
A_k: estimated peak amplitude of an isolated bin-centred real sinusoid, in the input signal's units
X_w[k]: unnormalised DFT coefficient after multiplying each input sample by its window weight
|X_w[k]|: magnitude of the complex coefficient at bin k
k: interior positive-frequency bin at which the mirrored negative-frequency tone contributes zero or negligibly; this condition must be checked for the window used
Σ: add w[n] from integer n of 0 through N − 1
w[n]: unitless window weight at sample n
n: integer sample index
N: input and window length in samples
In words: the sum of the weights replaces the record length in coherent tone-amplitude calibration.
```

## Complete Python example

The signal is a unitless, two-unit peak cosine at bin 8 of 64. `x * w` multiplies matching array elements.

```python
import numpy as np
from scipy.signal.windows import hann

n = np.arange(64)
x = 2 * np.cos(2 * np.pi * 8 * n / 64)
w = hann(64, sym=False)
X = np.fft.rfft(x * w)
print(w.mean())
print(round(2 * abs(X[8]) / w.sum(), 6))
# Corrected peak amplitude, not a PSD.
```

The outputs are `0.5` and `2.0`. A symmetric Hann of length 64 instead has mean 0.4921875. Calculate the actual weight sum when changing conventions.

Noise PSD calibration uses the sum of squared weights and sample rate, not simply the coherent gain. For general noisy measurements, use a documented PSD estimator and record its settings.

## Key takeaways

- Leakage can arise from the record boundary even without measurement noise.
- A taper trades main-lobe width against side-lobe suppression.
- Use the actual window sum for coherent tone amplitude, and a density normalisation for noise PSD.

## Further reading

- [SciPy: Hann conventions and definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hann.html)
- [Steven W. Smith: applications of the DFT](https://www.dspguide.com/CH9.PDF)
- [SciPy: periodogram density normalisation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html)
- [SciPy: window sums and spectral scaling](https://docs.scipy.org/doc/scipy/tutorial/signal.html#spectral-analysis)
