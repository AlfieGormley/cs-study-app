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

The Hann window NumPy uses is a smooth raised-cosine taper.

The window tapers the capture towards zero at both ends, reducing the artificial jump caused by analysing a finite segment. For an even-length Hann window, the centre gets just below one rather than exactly one.

Windowing also reduces the measured magnitude. To recover a bin-centred sine’s amplitude, account for the actual window sum. Ordinary positive-frequency bins need doubling because the real sine has a mirrored negative-frequency contribution:

```formula reference
A = 2 × |X[k]| / Σ w[n]
where
A: the amplitude of a sine whose frequency sits on bin k
X[k]: the raw complex FFT output for bin k
|X[k]|: its magnitude (size), which numpy gives with np.abs
k: the bin index
Σ w[n]: sigma means add all the window values: the sample count without a taper, and about half that count for Hann
w[n]: the window value for sample n
n: the sample index
In words: To measure a bin-centred sine, divide its FFT magnitude by the sum of the window and double ordinary positive-frequency bins. Do not double zero frequency or the even-length Nyquist bin.
```

The 0 Hz bin and, for even capture lengths, the Nyquist bin have no separate mirror, so they are not doubled; the `spectrum` function below halves them back.

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
