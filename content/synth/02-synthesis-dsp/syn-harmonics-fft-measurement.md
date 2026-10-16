---
id: syn-harmonics-fft-measurement
title: Measuring harmonics with an FFT
level: intermediate
minutes: 4
summary: Measuring harmonics with an FFT.
sourceLesson: syn-harmonics
---

## Check it with numpy

The roadmap asks you to compare spectra with an existing analysis tool rather than writing an FFT. numpy's `rfft` computes the discrete Fourier transform of a real signal.

The FFT reports the signal's content in a row of evenly spaced frequency slots called **bins**. Their spacing, and which bin holds a given frequency, follow from the sample rate and the number of samples analysed:

```formula
Δf = f_s / N
k = f / Δf = (fN) / f_s
Δf = 48000 Hz / 48000 = 1 Hz
where
Δf: delta f, the spacing between neighbouring bins, in hertz (Hz)
f_s: the sample rate, in Hz, here 48,000
N: the number of samples analysed, here 48,000 (one second)
k: the bin index (position in the output array) that holds frequency f
f: the frequency you want to look up, in Hz
Hz: hertz, cycles per second
In words: the bins are the sample rate divided by the analysis length apart; analyse one second and they are exactly 1 Hz apart, so bin number equals frequency in hertz.
```

This is **coherent sampling**: make the test components complete whole cycles in the capture. A useful trick follows: analyse exactly **one second** at an **integer** frequency. Then the FFT bins are exactly 1 Hz apart and every harmonic lands exactly on a bin, so there is no **spectral leakage** (energy smearing into neighbouring bins) to worry about. Half a second (24,000 samples) would give 2 Hz bins, so 300 Hz would be in bin 150.

```python
import numpy as np

fs, f0 = 48000, 100
n = np.arange(fs)                # 1 s
p = (f0 * n / fs) % 1.0          # phase
waves = {
  "saw": 2 * p - 1,
  "square": np.where(p < 0.5, 1.0, -1.0),
  "tri": 1 - 4 * np.abs(p - 0.5),
}
for name, x in waves.items():
    # Peak amplitudes of interior real bins.
    X = np.abs(np.fft.rfft(x)) * 2 / len(x)
    # Compare seven harmonics to the first.
    amps = X[f0 * np.arange(1, 8)]  # bin=Hz
    print(name, np.round(amps / amps[0], 3))
```

Output (harmonics 1 to 7, relative to the fundamental):

```
saw [1. 0.5 0.333 0.25 0.2 0.167 0.143]
square [1. 0. 0.333 0. 0.2 0. 0.143]
tri [1. 0. 0.111 0. 0.04 0. 0.02]
```

(Spacing tidied to fit; values unchanged.) The inverse-harmonic-number, odd-only and reciprocal-square harmonic patterns appear to the displayed precision. These are sampled naive waveforms, so small discretisation and folded-harmonic effects remain; this experiment does not prove exact band-limiting. The absolute fundamental amplitudes come out as 0.6366, 1.2732 and 0.8106, matching the leading factors of the three series above.

Note the scaling: `rfft` returns sums, not amplitudes. For a coherent real sine in an interior positive-frequency bin, multiply its magnitude by twice the reciprocal of the sample count. Do not double DC or the Nyquist endpoint, which do not have separate negative-frequency partners:

```formula
A = 2 × |X[k]| / N
|X[k]| = (NA) / 2 = 48000 × 0.5 / 2 = 12000
where
A: the amplitude (peak height) of the sine at bin k
X[k]: the complex number the FFT returns for bin k
k: the integer interior positive-frequency bin index; neither DC nor the Nyquist endpoint
|X[k]|: its magnitude (size), ignoring phase
N: the number of samples analysed, here 48,000
2: accounts for a real sine's energy being split equally between a positive and a negative frequency
In words: divide the raw bin magnitude by half the number of samples to get the sine's amplitude.
```

So one second of a 0.5-amplitude sine gives a raw magnitude of 12,000, and 2 × 12,000 / 48,000 brings it back to 0.5. For non-coherent frequencies or real recordings, a window such as `np.hanning` reduces sidelobe leakage while broadening peaks. Correct for its coherent gain if estimating amplitudes. Finite recordings and modulated sounds need a measurement method matched to the question.

## Key takeaways

- Bin spacing depends on analysis length, not just sample rate.
- Coherent steady test tones avoid leakage; windowing changes the measurement trade-off.
- Double interior positive-frequency magnitudes only when converting a real tone to peak amplitude.

## Further reading

- [Real FFT — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [FFT definitions and normalisation — NumPy](https://numpy.org/doc/stable/reference/routines.fft.html)
- [Spectrum analysis windows — Julius O. Smith](https://ccrma.stanford.edu/~jos/sasp/Spectrum_Analysis_Windows.html)
