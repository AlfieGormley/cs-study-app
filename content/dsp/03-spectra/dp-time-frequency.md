---
id: dp-time-frequency
title: Following frequencies through time
level: intermediate
minutes: 4
summary: Build a short-time spectrum and distinguish frame duration, hop spacing and frequency-grid spacing.
---

A single FFT mixes together everything that happens during its record. A sensor might vibrate at one frequency first and another later. To follow that change, analyse successive short records called **analysis frames**, or frames. A **short-time Fourier transform**, or **STFT**, is the collection of these windowed transforms.

A **spectrogram** displays a squared-magnitude or power-related version of the STFT, with time along one axis, frequency along another and strength represented by colour. Check its units and scaling: a coloured plot is not automatically a calibrated PSD.

## Frame length and hop do different things

The **hop** is the number of samples between neighbouring frame starts. Frames overlap when the hop is shorter than the frame length. A smaller hop gives more frequent updates; it does not shorten the observation inside each frame.

```formula
T_w = L / F_s
T_h = H / F_s
Δf = F_s / M
T_w = 128 / (1024 Hz) = 0.125 s
T_h = 32 / (1024 Hz) = 0.03125 s
Δf = 1024 Hz / 128 = 8 Hz
where
T_w: frame observation duration, in seconds (s)
T_h: interval between consecutive frame starts, in s
L: frame length, here 128 acquired samples
H: hop length, here 32 samples
F_s: sample rate, here 1024 hertz (Hz)
M: FFT length for each frame, here 128, with no zero padding
Δf: frequency-grid spacing for each frame, in Hz
Hz: hertz, cycles per second
s: second, the unit of time
In words: each spectrum observes 125 milliseconds even though a new frame starts every 31.25 milliseconds.
```

Longer frames give narrower spectral features for steady tones but mix changes over a longer time. Shorter frames localise changes better but broaden the features. More overlap cannot undo that trade-off. An abrupt change inside a frame can contribute both frequencies to that frame.

> [!analogy] Real-world analogy: overlapping snapshots
> Take long-exposure photographs at frequent intervals. Starting another exposure sooner creates more photographs, but each photograph still blends movement over its own exposure.
>
> **How it maps:** Frame length is the observation span and hop is the interval between observations. Overlapping frames share samples.
>
> **Where it stops:** The STFT measures oscillation components using a window, rather than brightness. A smaller hop cannot improve the window's intrinsic frequency discrimination.

## Complete Python example

This transparent STFT loop uses complete frames only: no boundary extension and no final partial frame. The first 256 dimensionless samples contain 64 Hz; the next 256 contain 192 Hz. Times label frame starts, not centres. Each row of `S` is one amplitude spectrum.

```python
import numpy as np
from scipy.signal.windows import hann

fs, size, hop = 1024, 128, 32
n = np.arange(512)
x = np.cos(2 * np.pi * 64 * n / fs)
x[256:] = np.cos(
    2 * np.pi * 192 * n[256:] / fs)
w = hann(size, sym=False)
starts = range(0, len(x) - size + 1, hop)
rows = []
for start in starts:
    X = np.fft.rfft(x[start:start+size]*w)
    a = abs(X) / w.sum()
    a[1:-1] *= 2
    rows.append(a)
S = np.array(rows)
f = np.fft.rfftfreq(size, 1 / fs)
print(S.shape)
print(f[np.argmax(S[[0, -1]], axis=1)])
```

The outputs are `(13, 65)` and `[ 64. 192.]`: thirteen complete frames, each with sixty-five real-spectrum bins. A production STFT API may centre frames or pad edges; choose and record those policies before comparing times. SciPy's `ShortTimeFFT` provides a configurable implementation; the loop makes the boundary and time-label choices visible.

## Key takeaways

- An STFT applies a windowed transform to many frames.
- Frame length controls the observation span; hop controls update spacing.
- Record frame timing, boundary handling and magnitude/power scaling with every spectrogram.

## Further reading

- [SciPy: short-time Fourier transform and frame parameters](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html)
- [SciPy: ShortTimeFFT](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html)
