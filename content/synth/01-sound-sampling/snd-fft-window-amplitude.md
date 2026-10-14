---
id: snd-fft-window-amplitude
title: Window and scale FFT amplitudes
level: advanced
minutes: 4
summary: Use a Hann window and the window sum to recover a bin-centred sine’s amplitude.
sourceLesson: snd-measuring
---

Analyse a real sample array with NumPy's `rfft`. In this unit, the capture length is the number of input samples and bins are indexed from zero. A bin-centred sine completes a whole number of cycles in the capture.

## Window and scale an FFT

The Hann window numpy uses is a single raised cosine, zero at both ends and 1 (or, for an even number of samples, just under 1) in the middle:

```formula
w[n] = 0.5 − 0.5 × cos(2 × π × n / (N − 1))
where
w[n]: the window value for sample n, between 0 and 1
n: the sample index, 0 to N − 1
N: the number of samples in the capture
cos: the cosine function, taking radians
π: pi, about 3.14159
In words: the window rises smoothly from 0 at the first sample to 1 in the middle and falls back to 0 at the last, so the capture has no abrupt start or end.
```

And the scaling that turns a bin's raw magnitude into a sine's amplitude:

```formula
A = 2 × |X[k]| / Σ w[n]
A = 2 × 12000 / 48000 = 0.5
where
A: the amplitude of a sine whose frequency sits on bin k
X[k]: the raw complex FFT output for bin k
|X[k]|: its magnitude (size), which numpy gives with np.abs
k: the bin index
Σ w[n]: the sum of all the window values; N for no window, about N/2 for Hann
w[n]: the window value for sample n
n: the sample index
In words: double the bin's magnitude (half the sine's energy sits in a mirrored negative frequency that rfft doesn't return) and divide by the sum of the window. Here, no window, 48,000 samples and a raw magnitude of 12,000 give an amplitude of 0.5.
```

The 0 Hz bin and (for even N) the Nyquist bin have no mirror, so they are not doubled; the `spectrum` function below halves them back.

```python
import numpy as np

def spectrum(x, fs):
    w = np.hanning(len(x))
    # Taper the ends before the transform.
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(len(x), 1/fs)
    # scale so a sine of amplitude A reads A
    # Correct the window’s amplitude loss.
    mag = np.abs(X) * 2 / np.sum(w)
    mag[0] *= 0.5  # DC has no mirror
    if len(x) % 2 == 0:
        mag[-1] *= 0.5  # Nyquist too
    return freqs, mag

fs = 48_000
n = np.arange(fs)
x = 0.5 * np.sin(2*np.pi*997*n/fs)
freqs, mag = spectrum(x, fs)
# Locate the strongest frequency bin.
k = np.argmax(mag)
print(f"bin width {freqs[1]:.1f} Hz")
print(f"peak at {freqs[k]:.1f} Hz,"
      f" {20*np.log10(mag[k]):.2f} dBFS")
```

```text
bin width 1.0 Hz
peak at 997.0 Hz, -6.02 dBFS
```

Both the frequency and the level match what we generated: the round trip from theory to data and back works.

## Key takeaways

- A Hann window tapers the capture endpoints to reduce abrupt boundaries.
- Divide FFT magnitude by the window sum and double ordinary positive-frequency bins.
- DC and the even-length Nyquist bin are not doubled; accurate bin-level readings assume a bin-centred tone.

## Further reading

- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [numpy.fft.rfftfreq — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html)
- [Spectrum Analysis Windows — Julius O. Smith, Spectral Audio Signal Processing (CCRMA)](https://ccrma.stanford.edu/~jos/sasp/Spectrum_Analysis_Windows.html)
- [numpy.hanning — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.hanning.html)
