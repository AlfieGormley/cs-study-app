---
id: snd-spectral-leakage
title: Leakage and tones between bins
level: advanced
minutes: 3
summary: Compare rectangular and Hann captures and explain why between-bin peak readings understate amplitude.
sourceLesson: snd-measuring
---

FFT bin spacing is the sample rate divided by the capture length in samples. The preceding FFT units explain the amplitude scaling; here we compare what happens when a tone falls between bins.

## Leakage between FFT bins

What if the frequency falls *between* bins? With a 0.1 s capture (10 Hz bins), compare 1000 Hz (exactly on a bin) with 1005 Hz (halfway between two bins), with and without a window:

```python
import numpy as np
fs, N = 48_000, 4_800          # 0.1 s
n = np.arange(N)
wins = {"rect": np.ones(N),
        "hann": np.hanning(N)}
for f in (1000.0, 1005.0):
    x = 0.5 * np.sin(2*np.pi*f*n/fs)
    for name, w in wins.items():
        mag = np.abs(np.fft.rfft(x*w))
        # Compare amplitudes on one scale.
        mag = mag * 2 / np.sum(w)
        db = 20*np.log10(mag + 1e-12)
        # Floor tiny magnitudes at -120 dB.
        db = np.maximum(db, -120)
        pk = db.max()
        far = db[150]        # 1.5 kHz
        print(f"{f:.0f} {name}:",
              f"peak {pk:6.2f},",
              f"1.5k {far:6.1f}")
```

```text
1000 rect: peak  -6.02, 1.5k -120.0
1000 hann: peak  -6.02, 1.5k -120.0
1005 rect: peak  -9.92, 1.5k  -51.8
1005 hann: peak  -7.44, 1.5k -117.7
```

(−120 here means "at or below −120 dB"; the floor hides meaningless rounding noise.)

- On a bin, both are perfect.
- Between bins, the **unwindowed** ("rect") capture loses 3.9 dB at the peak and leaks energy to −52 dB as far as 500 Hz away, which would mask real low-level components such as aliases.
- The **Hann** window loses only 1.4 dB at the peak and keeps the far leakage near −118 dB.

A between-bin amplitude shortfall is called **scalloping loss**. For accurate amplitudes, use coherent sampling (whole cycles), a flat-top window (which widens the main peak), or a peak-interpolation method with an amplitude correction matched to the chosen window.

Practical consequences: window when leakage is a concern; a rectangular window is suitable for a coherent capture containing whole cycles. Read levels from a capture long enough that the bins are fine; and when you need an exact level, generate test frequencies that land on bins (an integer number of cycles in the capture).

## Key takeaways

- An unwindowed, between-bin tone leaks energy into distant bins and can hide faint components.
- A Hann window reduces distant leakage, but a between-bin peak still underreads amplitude.
- For an exact level check, capture a whole number of cycles and use the correct scaling.

## Further reading

- [Spectrum Analysis Windows — Julius O. Smith, Spectral Audio Signal Processing (CCRMA)](https://ccrma.stanford.edu/~jos/sasp/Spectrum_Analysis_Windows.html)
- [Window function — Wikipedia](https://en.wikipedia.org/wiki/Window_function)
- [Spectral leakage — Wikipedia](https://en.wikipedia.org/wiki/Spectral_leakage)
- [Flat-top amplitude measurement — SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.flattop.html)
