---
id: syn-harmonics
title: Harmonics, spectra and timbre
level: intermediate
minutes: 12
summary: Why a sawtooth sounds different from a square or triangle at the same pitch, the 1/n and 1/n² harmonic patterns that define them, and how to check them yourself with numpy's FFT.
---

Play a sine, a triangle, a square and a sawtooth at the same pitch and loudness. Each sounds clearly different: the sine pure, the triangle soft, the square hollow, the saw buzzy and bright. Pitch and loudness are equal, so the difference is **timbre**, and for steady periodic tones timbre is largely set by the **spectrum**: which frequencies are present, and how strong each one is.

This lesson gives you the spectra of the standard waveforms and a way to verify them. Every later block (band-limiting, filters) is easier to reason about in these terms.

## Fourier series: any periodic wave is a sum of sines

A waveform that repeats every `T` seconds, at frequency `f0 = 1/T`, can be written as a sum of sine waves at whole-number multiples of `f0`:

```
x(t) = DC + Σ A_n·sin(2π·n·f0·t + φ_n)
       n=1,2,3...
```

- `DC` is the mean value (zero for the centred waveforms here).
- `n = 1` is the **fundamental**; perceived pitch need not equal the strongest component.
- `n = 2, 3, 4...` are the **harmonics** (or overtones) at 2f0, 3f0, 4f0...
- `A_n` is each harmonic's **amplitude**, and `φ_n` its **phase**.

This is the **Fourier series**. Intuitively: a sine is the only waveform with a single frequency, so anything more complicated must be several sines added together. The sharper the features of a waveform (corners, jumps), the more high harmonics it needs to build them.

The *magnitudes* `A_n` plotted against frequency form the **magnitude spectrum**: a row of spikes at multiples of `f0`, each with a height.

## The standard waveforms

| Wave | Harmonics present | Amplitude of n |
|---|---|---|
| Sine | 1 only | — |
| Saw | all (1, 2, 3...) | 1/n |
| Square | odd (1, 3, 5...) | 1/n |
| Triangle | odd (1, 3, 5...) | 1/n² |

For waves swinging between −1 and +1, the standard series are:

```
saw:  (2/π)  * Σ ±sin(n·ω·t) / n
      all n, alternating sign
square: (4/π) * Σ sin(n·ω·t) / n
      odd n
tri:  (8/π²) * Σ ±sin(n·ω·t) / n²
      odd n, alternating sign
```

(ω = 2π·f0, with time measured from a zero crossing of the wave. The alternating signs are phases; they shape the waveform but not the magnitude spectrum. The sign of the saw series depends on whether it ramps up or down.)

What this means for the sound:

- **Saw** has every harmonic, falling at 6 dB per octave of harmonic number (each doubling of `n` halves the amplitude). This is the brightest standard wave and the usual starting point for subtractive brass, strings and basses.
- **Square** has only odd harmonics at the same 1/n rate. Missing even harmonics give its hollow, woody, clarinet-like character.
- **Triangle** also has only odd harmonics, but they fall at 1/n², i.e. 12 dB per octave. The 3rd harmonic is 1/9 of the fundamental (−19 dB), so it sounds close to a sine.

> [!note] Pulse waves
> A pulse of width `w` has harmonic amplitudes proportional to `|sin(π·n·w)| / n`. Wherever `n·w` is a whole number, that harmonic vanishes. At `w = 0.5` all even harmonics vanish (a square). At `w = 0.25` every 4th harmonic vanishes. This is why sweeping pulse width changes the timbre so audibly.

## Check it with numpy

The roadmap asks you to compare spectra with an existing analysis tool rather than writing an FFT. numpy's `rfft` computes the discrete Fourier transform of a real signal.

A useful trick: analyse exactly **one second** at an **integer** frequency. Then the FFT bins are exactly 1 Hz apart and every harmonic lands exactly on a bin, so there is no leakage to worry about.

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
    X = np.abs(np.fft.rfft(x)) * 2 / len(x)
    amps = X[f0 * np.arange(1, 8)]  # bin=Hz
    print(name, np.round(amps / amps[0], 3))
```

Output (harmonics 1 to 7, relative to the fundamental):

```
saw [1. 0.5 0.333 0.25 0.2 0.167 0.143]
square [1. 0. 0.333 0. 0.2 0. 0.143]
tri [1. 0. 0.111 0. 0.04 0. 0.02]
```

(Spacing tidied to fit; values unchanged.) The 1/n, odd-only and 1/n² patterns appear exactly. The absolute fundamental amplitudes come out as 0.6366, 1.2732 and 0.8106, matching 2/π, 4/π and 8/π² from the series.

Note the scaling: `rfft` returns sums, so multiplying by `2 / N` converts a bin to the amplitude of a sine (the factor 2 accounts for the energy split between positive and negative frequencies). For non-integer frequencies or real recordings, apply a window (e.g. `np.hanning`) before the FFT and expect peaks to spread across neighbouring bins.

## Phase changes shape, not (much) timbre

Two waves can have identical magnitude spectra but different shapes. Build a 39-harmonic saw-like tone twice: once with all harmonics in sine phase, once all in cosine phase.

```python
import numpy as np

fs, f0 = 48000, 100
t = np.arange(fs) / fs

def build(phase):
    x = np.zeros(fs)
    for n in range(1, 40):   # 39 harmonics
        x += np.sin(2*np.pi*n*f0*t
                    + phase) / n
    return x

for ph in (0.0, np.pi / 2):  # sin vs cos
    x = build(ph)
    X = np.abs(np.fft.rfft(x)) * 2 / fs
    print(np.round(X[[100, 200, 300]], 3),
          round(np.abs(x).max(), 2))
```

```
[1.    0.5   0.333] 1.81
[1.    0.5   0.333] 4.25
```

Same harmonic amplitudes, but the cosine-phase version has a peak 2.3 times higher (about 7.4 dB), because all its harmonics line up at t = 0. For steady tones the ear is much more sensitive to the magnitudes than the phases, so the two sound very similar. Your **headroom** does not care what it sounds like: the peak is what clips. Filters change phases, which is one reason a filtered signal can peak higher than its input.

## Gibbs ripple

Adding up a finite number of harmonics never quite produces a perfect corner. A square wave built from odd harmonics overshoots each jump by about 9% of the jump size, however many harmonics you add (peaks of about 1.18 for a ±1 square). This is the **Gibbs phenomenon**. It matters later: a *band-limited* square or saw, the kind that doesn't alias, has these ripples by construction. They are correct, not a bug.

## Timbre is more than the static spectrum

The spectrum explains why waveforms differ, but real timbre also depends on how the spectrum **changes over time**. A piano's high harmonics die faster than its fundamental; a brass note gets brighter as it gets louder. That is why synths pair oscillators with filters, envelopes and modulation, which change the spectrum while the note plays. The DSP learning objectives ask you to describe a target sound in exactly these terms: pitch, spectrum, envelope and modulation.

## Key takeaways

- A periodic wave consists of its DC mean plus sinusoids at multiples of its fundamental; their magnitudes form its spectrum.
- Saw: all harmonics at 1/n. Square: odd at 1/n. Triangle: odd at 1/n². Pulse: zeros where n·w is whole.
- Use `np.fft.rfft`, one second of signal and integer frequencies to read harmonic amplitudes exactly; scale by 2/N.
- Phase changes the waveform's shape and peak level, which matters for headroom, while changing the steady timbre little.
- Band-limited jumps ripple (Gibbs); timbre also depends on how the spectrum evolves over time.

## Further reading

- [Fourier series — Wikipedia](https://en.wikipedia.org/wiki/Fourier_series)
- [Sawtooth wave — Wikipedia](https://en.wikipedia.org/wiki/Sawtooth_wave)
- [Square wave — Wikipedia](https://en.wikipedia.org/wiki/Square_wave)
- [Triangle wave — Wikipedia](https://en.wikipedia.org/wiki/Triangle_wave)
- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [Mathematics of the Discrete Fourier Transform — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/mdft/)
- [Gibbs phenomenon — Wikipedia](https://en.wikipedia.org/wiki/Gibbs_phenomenon)
- [Timbre — Wikipedia](https://en.wikipedia.org/wiki/Timbre)
