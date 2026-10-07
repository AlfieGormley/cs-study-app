---
id: snd-measuring
title: Measuring audio offline
level: advanced
minutes: 16
summary: A Python workbench for checking audio by numbers, not just by ear. Generate test signals, plot them, read a spectrum with numpy's FFT, verify frequency and level, confirm an aliasing prediction, and write a WAV file with a library.
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
    return amp * np.sin(2*np.pi*f*n/fs)

x = tone(997)
print(len(x), x.dtype)
print(f"peak {np.max(np.abs(x)):.4f}")
rms = np.sqrt(np.mean(x**2))
print(f"rms  {rms:.4f}")
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
- **RMS** 0.3536 = 0.5/√2, the sine's crest factor.
- **DC offset** (the mean) should be essentially zero. A non-zero mean means the waveform is shifted off centre, which wastes headroom and can thump when audio starts and stops.

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

Plot **short windows** (a few cycles) to see the shape, and mark the samples as dots, because they're the real data. The lines joining them are just a drawing aid; recall from lesson 4 that the true reconstructed signal is smooth, not straight-sided. Fixing the y-axis at ±1 makes levels comparable between plots.

## Measure frequency in the time domain

For a clean, single-frequency signal, count **upward zero crossings**: places where a sample is negative and the next one isn't. Average the spacing between them:

```python
import numpy as np
fs = 48_000
n = np.arange(fs)
x = 0.5 * np.sin(2*np.pi*997*n/fs)

# upward zero crossings: - to + sign change
s = np.signbit(x)
ups = np.flatnonzero(s[:-1] & ~s[1:])
periods = np.diff(ups) / fs
print(f"{1 / np.mean(periods):.2f} Hz")
```

```text
997.01 Hz
```

This counts whole samples, so it's only accurate to a fraction of a sample per period (here 0.01 Hz after averaging many periods). It's fooled by noise and by waveforms with several crossings per cycle. For anything richer than a sine, use the spectrum.

## Read a spectrum with numpy's FFT

The **FFT** (fast Fourier transform) takes N samples and returns how much of each frequency they contain, at N/2 + 1 evenly spaced frequencies from 0 to fs/2 for real input (when N is even). Three facts you need to read it correctly:

1. **Bin spacing** is fs/N. One second at 48 kHz gives 1 Hz bins; 0.1 s gives 10 Hz bins. Longer captures give finer frequency resolution.
2. **Scaling:** numpy's raw output grows with N. To read a sine's amplitude directly, multiply by 2 and divide by the sum of the window (below).
3. **Windowing:** multiply the capture by a smooth **window** (Hann is a good default) that tapers its ends to zero. Without it, a frequency that doesn't fit a whole number of cycles in the capture smears energy across the spectrum. That smearing is called **spectral leakage**.

```python
import numpy as np

def spectrum(x, fs):
    w = np.hanning(len(x))
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(len(x), 1/fs)
    # scale so a sine of amplitude A reads A
    mag = np.abs(X) * 2 / np.sum(w)
    mag[0] *= 0.5  # DC has no mirror
    if len(x) % 2 == 0:
        mag[-1] *= 0.5  # Nyquist too
    return freqs, mag

fs = 48_000
n = np.arange(fs)
x = 0.5 * np.sin(2*np.pi*997*n/fs)
freqs, mag = spectrum(x, fs)
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

### Leakage and why the window matters

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
        mag = mag * 2 / np.sum(w)
        db = 20*np.log10(mag + 1e-12)
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

Practical consequences: always window; read levels from a capture long enough that the bins are fine; and when you need an exact level, generate test frequencies that land on bins (an integer number of cycles in the capture).

## Verify an aliasing prediction

Lesson 4 predicted where a naive 1,760 Hz sawtooth's harmonics fold at 48 kHz. Now measure it. A 1 s capture makes each bin exactly 1 Hz, so bin index equals frequency:

```python
import numpy as np

fs, f0 = 48_000, 1_760
n = np.arange(fs)                  # 1 s
phase = (f0 * n / fs) % 1.0
saw = 2 * phase - 1                # naive

w = np.hanning(fs)
X = np.fft.rfft(saw * w)
mag = np.abs(X) * 2 / w.sum()
db = 20 * np.log10(mag + 1e-12)
ref = db[f0]               # fundamental

for hz in (480, 1280, 2240, 3040, 3520):
    real = hz % f0 == 0
    kind = "harmonic" if real else "alias"
    rel = db[hz] - ref
    print(f"{hz:>5} Hz {rel:6.1f} dB",
          kind)
```

```text
  480 Hz  -28.5 dB alias
 1280 Hz  -28.8 dB alias
 2240 Hz  -28.2 dB alias
 3040 Hz  -29.1 dB alias
 3520 Hz   -6.0 dB harmonic
```

The predictions were −28.6, −28.9, −28.3 and −29.2 dB for the four aliases (1/k for harmonics 27, 28, 26 and 29), and −6.0 dB for the 2nd harmonic. The measurements agree to about 0.1 dB, and the small differences come from other, much weaker harmonics folding onto the same bins. This is the "compare a deliberately aliased signal with its predicted apparent frequency" exercise from the roadmap. Later, run the same script against a band-limited oscillator from a library and watch those aliases drop.

## Write a WAV file with a library

Writing a WAV encoder isn't a learning goal; a library handles the format. `soundfile` (a wrapper for libsndfile) takes float arrays and converts them to the requested **subtype**:

```python
import numpy as np
import soundfile as sf

fs = 48_000
n = np.arange(2 * fs)                # 2 s
# -12 dBFS sine
x = 0.25 * np.sin(2*np.pi*440*n/fs)

# 10 ms fades so the file doesn't click
ramp = np.linspace(0, 1, fs // 100)
x[:ramp.size] *= ramp
x[-ramp.size:] *= ramp[::-1]

x = np.clip(x, -1.0, 1.0)    # be explicit
sf.write("a440.wav", x, fs,
         subtype="PCM_24")

y, fs2 = sf.read("a440.wav")
info = sf.info("a440.wav")
print(fs2, info.subtype, len(y))
err = np.max(np.abs(y - x))
print(f"max error {err:.1e}")
```

```text
48000 PCM_24 96000
max error 1.2e-07
```

Reading the file back and comparing is the important habit. The sample rate, format and length are as intended, and the error is at most one 24-bit step (2⁻²³ ≈ 1.2 × 10⁻⁷). That's quantisation, not a bug. It's a full step rather than the half step that rounding would give because, in the libsndfile version bundled here (1.2.2), the clipping conversion rounds *down*: every error lies between 0 and −1 step. At 24 bits that's harmless, but it's exactly the kind of detail a read-back check reveals.

Notes:

- `sf.read` returns float64 in ±1.0 by default. Pass `dtype="int16"` or `"int32"` to get integers instead. These are scaled to fill the integer type, not the file's raw values: a 16-bit file read as int16 gives its stored samples, but a 24-bit file read as int32 comes back multiplied by 256.
- Use `subtype="FLOAT"` to keep a 32-bit float file with headroom above 1.0 for analysis. Use `PCM_16` or `PCM_24` for files to share or import into a DAW.
- `soundfile` switches on libsndfile's clipping option whenever it opens a file, so in testing it clipped 1.7 to full scale when writing PCM rather than wrapping it. **Clip explicitly** anyway, so your output never depends on a library setting.
- The fades matter: a file that starts or ends mid-wave clicks, which is easy to mistake for a synth bug.

## A measurement checklist

Before trusting any experiment's audio, check:

| Check | How |
|---|---|
| Length and rate | `len(x)`, `sf.info` |
| Finite values | `np.isfinite(x).all()` |
| Peak level | `20·log10(max abs)` |
| RMS and DC | `sqrt(mean(x²))`, `mean(x)` |
| Clipped samples | count `abs(x) >= 1` |
| Frequency | windowed FFT peak |
| Unwanted content | FFT, compare with prediction |

Then listen at a safe level. Measurement tells you what's there; listening tells you whether it matters.

## Key takeaways
- Verify by numbers: length, peak, RMS, DC, finiteness and clipped-sample count are one-liners.
- Plot short windows with sample dots; lines between dots aren't the real signal.
- FFT bin spacing is fs/N. Window the capture (Hann), and scale magnitudes by 2/sum(window) to read sine amplitudes.
- Leakage from unwindowed, between-bin frequencies can mask low-level components; windowing fixes most of it.
- Measured aliases matched the lesson 4 predictions to about 0.1 dB, which is the point: predict, then measure.
- Write WAVs with a library, clip explicitly, add short fades, and read the file back to check it.

## Further reading
- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [numpy.fft.rfftfreq — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html)
- [python-soundfile documentation](https://python-soundfile.readthedocs.io/)
- [Spectrum Analysis Windows — Julius O. Smith, Spectral Audio Signal Processing (CCRMA)](https://ccrma.stanford.edu/~jos/sasp/Spectrum_Analysis_Windows.html)
- [Window function — Wikipedia](https://en.wikipedia.org/wiki/Window_function)
- [Spectral leakage — Wikipedia](https://en.wikipedia.org/wiki/Spectral_leakage)
