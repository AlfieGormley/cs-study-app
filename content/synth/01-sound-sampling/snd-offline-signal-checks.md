---
id: snd-offline-signal-checks
title: Check and plot an offline test signal
level: advanced
minutes: 5
summary: Build a reproducible Python workbench and check signal length, level, DC and zero-crossing frequency.
sourceLesson: snd-measuring
---

Ears are good at telling you *something* is wrong and bad at telling you *what*. Is that buzz aliasing or clipping? Is the note 3 cents flat, or is it a filter making it sound duller? The roadmap's readiness test for this stage is to "explain each sample's meaning, verify frequency and level from the data". This lesson builds a small offline toolkit for doing exactly that.

The tools are standard: **numpy** for arrays and the FFT, **matplotlib** for plots, **soundfile** for WAV files. You're *using* an FFT, not writing one; FFT implementation is deliberately deferred.



## Set up

Use a virtual environment so the experiments are reproducible from a clean checkout:

```text
python3 -m venv .venv
. .venv/bin/activate
pip install numpy matplotlib soundfile
pip freeze > requirements.txt
```

Commit `requirements.txt` with your experiments. The outputs below were produced with numpy 2.5, matplotlib 3.11 and soundfile 0.14; numbers in the last decimal place may differ slightly on other versions.

> [!warning] Protect your ears and speakers
> A full-scale sine is very loud and fatiguing. Generate test files at −12 dBFS or lower, turn the monitor level down before playing anything new, and raise it gradually. Never play untested generated audio on headphones at volume.

## Generate a test signal and check it numerically

Start with a known signal and check that the numbers match the theory:

```python
import numpy as np

fs = 48_000

def tone(f, secs=1.0, amp=0.5, fs=fs):
    n = np.arange(int(secs * fs))
    # Sample index divided by rate is time.
    return amp * np.sin(2*np.pi*f*n/fs)

x = tone(997)
print(len(x), x.dtype)
print(f"peak {np.max(np.abs(x)):.4f}")
rms = np.sqrt(np.mean(x**2))
print(f"rms  {rms:.4f}")
# A whole-cycle sine should have no DC.
print("dc ok:", abs(np.mean(x)) < 1e-9)
```

```text
48000 float64
peak 0.5000
rms  0.3536
dc ok: True
```

Each check has a reason:

- **Length:** 1 s at 48 kHz must be 48,000 samples. Off-by-one-block errors show up here.
- **Peak** 0.5 is −6.02 dBFS, as requested.
- **RMS** 0.3536 is the peak divided by 1.414 (the square root of 2), the sine's crest factor (the peak-and-RMS unit).
- **DC offset** (the mean) should be essentially zero for this whole-cycle capture. Partial cycles can have a non-zero mean even when the underlying wave is centred correctly. A non-zero mean means the waveform is shifted off centre, which wastes headroom and can thump when audio starts and stops.

Other cheap sanity checks are worth wrapping in a function: `np.isfinite(x).all()` (NaN or infinity anywhere means a bug, often a filter blowing up), and the number of samples at or beyond ±1.0.

## Plot the waveform

A plot shows what summary numbers hide: discontinuities, glitches at block boundaries, asymmetry.

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")      # no window
import matplotlib.pyplot as plt

fs = 48_000
n = np.arange(480)             # 10 ms
x = 0.5 * np.sin(2*np.pi*440*n/fs)

# Plot sample times in milliseconds.
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(n / fs * 1000, x, marker=".",
        linewidth=0.8)
ax.set_xlabel("time (ms)")
ax.set_ylabel("amplitude")
ax.set_ylim(-1, 1)
ax.grid(True)
fig.savefig("sine.png", dpi=120)
print("saved sine.png")
```

```text
saved sine.png
```

Plot **short windows** (a few cycles) to see the shape, and mark the samples as dots, because they're the real data. The lines joining them are just a drawing aid; recall from the reconstruction unit that the true reconstructed signal is smooth, not straight-sided. Fixing the y-axis at ±1 makes levels comparable between plots.

## Measure frequency in the time domain

For a clean, single-frequency signal, count **upward zero crossings**: places where a sample is negative and the next one isn't. Average the spacing between them:

```python
import numpy as np
fs = 48_000
n = np.arange(fs)
x = 0.5 * np.sin(2*np.pi*997*n/fs)

# upward zero crossings: - to + sign change
s = np.signbit(x)
# Select negative-to-nonnegative crossings.
ups = np.flatnonzero(s[:-1] & ~s[1:])
# Crossing gaps become seconds per cycle.
periods = np.diff(ups) / fs
print(f"{1 / np.mean(periods):.2f} Hz")
```

```text
997.01 Hz
```

The frequency is one over the average period, where each period is measured in samples and converted to seconds:

```formula
f ≈ 1 / T_avg
T_avg = D_avg / fs
f ≈ 48000 / 48.144 ≈ 997.0 Hz
where
f: the estimated frequency, in hertz (Hz)
T_avg: the average time between upward zero crossings, in seconds (s)
D_avg: the average spacing between upward zero crossings, in samples; about 48.144 for 997 Hz at 48 kHz
fs: the sample rate, in samples per second; here 48,000
Hz: hertz, cycles per second
≈: approximately equal to (an estimate, then rounded)
In words: count the average number of samples between upward crossings, turn it into seconds, and take one over that.
```

This counts whole samples, so it's only accurate to a fraction of a sample per period (here 0.01 Hz after averaging many periods). It's fooled by noise and by waveforms with several crossings per cycle. For anything richer than a sine, use the spectrum.

## Key takeaways

- Check sample count, peak, RMS, DC offset and finiteness before listening at a safe level.
- Plot short windows with sample dots; joining lines are a visual aid.
- Upward zero crossings estimate a clean sine’s period but are unreliable on noisy or complex waveforms.

## Further reading

- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [python-soundfile documentation](https://python-soundfile.readthedocs.io/)
