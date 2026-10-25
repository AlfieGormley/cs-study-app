---
id: dp-zero-padding
title: More bins do not mean more observation
level: intermediate
minutes: 4
summary: Use zero padding to sample a spectrum more finely without mistaking it for new resolving power.
---

**Zero padding** appends zeros to a record before its FFT. The longer transform evaluates the same finite record's frequency response at more closely spaced frequencies. It can make a plotted peak smoother and improve a grid-based peak-frequency estimate. It adds no measurements.

**Frequency resolution** can mean several things. Always separate the displayed grid spacing from the ability to distinguish two neighbouring tones. Resolving close tones depends on the actual observation duration, window shape, relative amplitudes and noise. Zero padding changes only the grid.

## Two lengths with two jobs

The observation length counts acquired samples. The FFT length includes any appended zeros.

```formula
T = N / F_s
Δf = F_s / M
T = 64 / (640 Hz) = 0.1 s
Δf = 640 Hz / 256 = 2.5 Hz
where
T: acquired record duration in seconds (s), using N sample intervals
N: acquired sample count, here 64
F_s: sample rate, here 640 hertz (Hz)
M: FFT length, at least N; here 256 after appending 192 zeros
Δf: displayed FFT frequency-grid spacing, in Hz
Hz: hertz, cycles per second
s: second, the unit of time
In words: padding a tenth-second observation to 256 points gives a 2.5-hertz grid but still only a tenth-second observation.
```

The unpadded grid spacing is 10 Hz. Padding to four times the length gives four times as many grid intervals, while the window's main lobe keeps its physical width in hertz. To narrow that feature, collect a longer record of a signal that stays sufficiently steady, with a suitable window.

> [!analogy] Real-world analogy: enlarging a photograph
> Enlarging an existing photograph can make its shapes easier to inspect. It does not capture details that the camera never recorded.
>
> **How it maps:** Extra FFT points sample the existing finite-record spectrum more densely; extra acquired samples can supply new observation information.
>
> **Where it stops:** Zero padding is exact evaluation on a denser frequency grid, not a camera's pixel interpolation algorithm. Its usefulness and limitations follow from the record's transform.

## Complete Python example

A 73 Hz cosine falls between the unpadded 10 Hz bins. `rfft(x, n=256)` appends zeros internally. `argmax` returns the index of the largest magnitude. The normalisation still uses 64 acquired samples, not the padded length; this example reports frequencies only.

```python
import numpy as np

fs = 640
n = np.arange(64)
x = np.cos(2 * np.pi * 73 * n / fs)
for size in (64, 256):
    X = np.fft.rfft(x, n=size)
    f = np.fft.rfftfreq(size, 1 / fs)
    print(f[np.argmax(abs(X))])
# Denser peak search, same acquired data.
```

The peak-grid labels are `70.0` and `72.5` Hz. The closer second label is useful, but it is not proof of 2.5 Hz measurement accuracy. Leakage, the finite record and nearby signals can bias a peak estimate. No universal separation threshold follows from the grid alone.

If a tapered record is padded, amplitude normalisation uses the sum of the original window weights. Including the appended zeros in a simple record-length denominator would falsely reduce the inferred amplitude.

## Key takeaways

- Keep acquired sample count and FFT length separate.
- Zero padding changes grid spacing, not observation duration or the window's main-lobe width in hertz.
- A denser peak label is an estimate, with uncertainty beyond grid spacing.

## Further reading

- [NumPy: FFT length and zero padding](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [Steven W. Smith: Fourier transform properties](https://www.dspguide.com/CH10.PDF)
