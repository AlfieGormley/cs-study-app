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

A waveform that repeats at a fixed interval (its period) has a fundamental frequency of one divided by that period, and it can be written as a sum of sine waves at whole-number multiples of that frequency:

```formula
f_0 = 1 / T
x(t) = DC + Σ A_n × sin(2π·n·f_0·t + φ_n)
where
f_0: the fundamental frequency, in hertz (Hz): how many times per second the waveform repeats
T: the period, the time one repeat takes, in seconds (s)
x(t): the value of the waveform at time t
t: time, in seconds (s)
DC: the waveform's mean (average) value, a constant offset; zero for the centred waveforms here
Σ: sigma, "sum of": add up the term after it for n = 1, 2, 3 and so on (in principle for ever)
n: the harmonic number, a whole number 1, 2, 3...; component n has frequency n × f_0
A_n: the amplitude (peak height) of component n
sin: the sine function, taking an angle in radians
π: pi, about 3.14159; 2π radians is one full cycle
φ_n: phi n, the phase of component n: where in its cycle that sine starts, in radians
·: multiplication, the same as ×
Hz: hertz, cycles per second
s: seconds
In words: any repeating wave equals its average plus a stack of sines at 1, 2, 3... times the repeat rate, each with its own height and starting point.
```

For example, a wave repeating every 10 ms (T = 0.01 s) has f_0 = 100 Hz, so its components can only be at 100, 200, 300 Hz and so on.

- DC is the mean value (zero for the centred waveforms here).
- n = 1 is the **fundamental**; perceived pitch need not equal the strongest component.
- n = 2, 3, 4... are the **harmonics** (or overtones) at 2, 3, 4... times f_0.
- A_n is each harmonic's **amplitude**, and φ_n its **phase**.

This is the **Fourier series**. Intuitively: a sine is the only waveform with a single frequency, so anything more complicated must be several sines added together. The sharper the features of a waveform (corners, jumps), the more high harmonics it needs to build them.

The *magnitudes* A_n plotted against frequency form the **magnitude spectrum**: a row of spikes at multiples of `f0`, each with a height.

## The standard waveforms

| Wave | Harmonics present | Amplitude of n |
|---|---|---|
| Sine | 1 only | — |
| Saw | all (1, 2, 3...) | 1/n |
| Square | odd (1, 3, 5...) | 1/n |
| Triangle | odd (1, 3, 5...) | 1/n² |

For waves swinging between −1 and +1, the standard series are:

```formula
ω = 2π × f_0
x_saw(t) = (2/π)
  × Σ (−1)^{n+1} × sin(n·ω·t) / n
x_sq(t) = (4/π) × Σ sin(n·ω·t) / n
x_tri(t) = (8/π^2)
  × Σ (−1)^{k} × sin(n·ω·t) / n^2
where
ω: omega, the angular frequency of the fundamental, in radians per second: 2π radians per cycle times f_0 cycles per second
f_0: the fundamental frequency, in hertz (Hz)
π: pi, about 3.14159
x_saw(t), x_sq(t), x_tri(t): the sawtooth, square and triangle waves at time t, each between −1 and +1
t: time in seconds, measured from a point where the wave crosses zero going upwards
Σ: sigma, "sum of": for the saw add the term for every n = 1, 2, 3...; for the square and triangle add it for odd n only (1, 3, 5...)
n: the harmonic number
sin: the sine function, taking an angle in radians
(−1)^{n+1}: a sign that alternates +, −, +, − for n = 1, 2, 3, 4...
k: for the triangle, (n − 1) / 2, so (−1)^{k} alternates +, −, + for n = 1, 3, 5
·: multiplication, the same as ×
Hz: hertz, cycles per second
In words: the saw has every harmonic at 1/n of the fundamental's strength, the square has only odd harmonics at 1/n, and the triangle has only odd harmonics at the much faster-falling 1/n^2.
```

The factors in front (2/π ≈ 0.637, 4/π ≈ 1.273 and 8/π^2 ≈ 0.811) are the amplitudes of each wave's fundamental. The alternating signs are phases; they shape the waveform but not the magnitude spectrum. The sign of the saw series depends on whether it ramps up or down; this one ramps up.

To compare harmonics by ear it helps to convert their relative amplitudes into decibels:

```formula
L = 20 × log_10(A_n / A_1)
L = 20 × log_10(1/2) ≈ −6.0 dB
L = 20 × log_10(1/9) ≈ −19.1 dB
where
L: the level of harmonic n relative to the fundamental, in decibels (dB); negative means quieter
A_n: the amplitude of harmonic n
A_1: the amplitude of the fundamental
log_10: the base-10 logarithm: the power you raise 10 to to get the number, so log_10(0.1) = −1
20: the factor that converts an amplitude ratio to decibels
dB: decibels
≈: approximately equal to
In words: halving an amplitude is about −6 dB; the saw's 2nd harmonic (1/2) is −6 dB and the triangle's 3rd (1/9) is about −19 dB.
```

What this means for the sound:

- **Saw** has every harmonic, falling at 6 dB per octave of harmonic number (each doubling of the harmonic number halves the amplitude). This is the brightest standard wave and the usual starting point for subtractive brass, strings and basses.
- **Square** has only odd harmonics at the same 1/n rate. Missing even harmonics give its hollow, woody, clarinet-like character.
- **Triangle** also has only odd harmonics, but they fall at 1/n², i.e. 12 dB per octave. The 3rd harmonic is 1/9 of the fundamental (−19 dB), so it sounds close to a sine.

### Pulse waves

A pulse wave's harmonics depend on its width (the fraction of each cycle it spends high):

```formula
A_n ∝ |sin(π × n × w)| / n
where
A_n: the amplitude of harmonic n
∝: "is proportional to": A_n equals the right-hand side times a fixed scale factor
|x|: the absolute value of x, i.e. x without its sign
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
n: the harmonic number, 1, 2, 3...
w: the pulse width, a fraction of the cycle between 0 and 1 (0.5 is a square wave)
In words: each harmonic's strength falls roughly as 1/n, but is multiplied by a sine that reaches zero whenever n × w is a whole number.
```

Wherever n × w is a whole number, sin(π × n × w) is zero and that harmonic vanishes. At w = 0.5 all even harmonics vanish (a square). At w = 0.25 every 4th harmonic vanishes: for n = 4, n × w = 1. This is why sweeping pulse width changes the timbre so audibly.

## Check it with numpy

The roadmap asks you to compare spectra with an existing analysis tool rather than writing an FFT. numpy's `rfft` computes the discrete Fourier transform of a real signal.

The FFT reports the signal's content in a row of evenly spaced frequency slots called **bins**. Their spacing, and which bin holds a given frequency, follow from the sample rate and the number of samples analysed:

```formula
Δf = f_s / N
k = f / Δf = f × N / f_s
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

A useful trick follows: analyse exactly **one second** at an **integer** frequency. Then the FFT bins are exactly 1 Hz apart and every harmonic lands exactly on a bin, so there is no **spectral leakage** (energy smearing into neighbouring bins) to worry about. Half a second (24,000 samples) would give 2 Hz bins, so 300 Hz would be in bin 150.

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

(Spacing tidied to fit; values unchanged.) The 1/n, odd-only and 1/n² patterns appear exactly. The absolute fundamental amplitudes come out as 0.6366, 1.2732 and 0.8106, matching the leading factors of the three series above.

Note the scaling: `rfft` returns sums, not amplitudes, so the code multiplies by `2 / N`:

```formula
A = 2 × |X[k]| / N
|X[k]| = N × A / 2 = 48000 × 0.5 / 2 = 12000
where
A: the amplitude (peak height) of the sine at bin k
X[k]: the complex number the FFT returns for bin k
|X[k]|: its magnitude (size), ignoring phase
N: the number of samples analysed, here 48,000
2: accounts for a real sine's energy being split equally between a positive and a negative frequency
In words: divide the raw bin magnitude by half the number of samples to get the sine's amplitude.
```

So one second of a 0.5-amplitude sine gives a raw magnitude of 12,000, and 2 × 12,000 / 48,000 brings it back to 0.5. For non-integer frequencies or real recordings, apply a window (e.g. `np.hanning`) before the FFT and expect peaks to spread across neighbouring bins.

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

Same harmonic amplitudes, but the cosine-phase version has a peak 2.3 times higher, because all its harmonics reach their crests together at the start of each cycle. In decibels:

```formula
ΔL = 20 × log_10(P_2 / P_1)
ΔL = 20 × log_10(4.25 / 1.81) ≈ 7.4 dB
where
ΔL: delta L, the difference in peak level, in decibels (dB)
P_1: the peak of the sine-phase version, 1.81
P_2: the peak of the cosine-phase version, 4.25
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to
In words: lining up the harmonics' crests raised the peak by about 7.4 dB without changing any harmonic's amplitude.
```

For steady tones the ear is much more sensitive to the magnitudes than the phases, so the two sound very similar. Your **headroom** does not care what it sounds like: the peak is what clips. Filters change phases, which is one reason a filtered signal can peak higher than its input.

## Gibbs ripple

Adding up a finite number of harmonics never quite produces a perfect corner. A square wave built from odd harmonics overshoots each jump by about 9% of the jump size, however many harmonics you add:

```formula
P ≈ 1 + 0.09 × J
P ≈ 1 + 0.09 × 2 ≈ 1.18
where
P: the peak value of the band-limited square, which ideally would be 1
J: the size of the jump, from −1 to +1, so 2
0.09: the Gibbs overshoot, about 9% (more precisely 8.95%) of the jump
≈: approximately equal to
In words: a ±1 square made from a finite number of harmonics peaks at about 1.18, so it needs about 1.4 dB more headroom than the ideal square.
```

This is the **Gibbs phenomenon**. It matters later: a *band-limited* square or saw, the kind that doesn't alias, has this Gibbs ripple by construction. It is correct, not a bug.

## Timbre is more than the static spectrum

The spectrum explains why waveforms differ, but real timbre also depends on how the spectrum **changes over time**. A piano's high harmonics die faster than its fundamental; a brass note gets brighter as it gets louder. That is why synths pair oscillators with filters, envelopes and modulation, which change the spectrum while the note plays. The DSP learning objectives ask you to describe a target sound in exactly these terms: pitch, spectrum, envelope and modulation.

## Key takeaways

- A periodic wave consists of its DC mean plus sinusoids at multiples of its fundamental; their magnitudes form its spectrum.
- Saw: all harmonics at 1/n. Square: odd at 1/n. Triangle: odd at 1/n². Pulse: a harmonic vanishes wherever its number times the width is a whole number.
- Use `np.fft.rfft`, one second of signal and integer frequencies to read harmonic amplitudes exactly; scale by 2/N.
- Phase changes the waveform's shape and peak level, which matters for headroom, while changing the steady timbre little.
- Band-limited jumps show Gibbs ripple; timbre also depends on how the spectrum evolves over time.

## Further reading

- [Fourier series — Wikipedia](https://en.wikipedia.org/wiki/Fourier_series)
- [Sawtooth wave — Wikipedia](https://en.wikipedia.org/wiki/Sawtooth_wave)
- [Square wave — Wikipedia](https://en.wikipedia.org/wiki/Square_wave)
- [Triangle wave — Wikipedia](https://en.wikipedia.org/wiki/Triangle_wave)
- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [Mathematics of the Discrete Fourier Transform — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/mdft/)
- [Gibbs phenomenon — Wikipedia](https://en.wikipedia.org/wiki/Gibbs_phenomenon)
- [Timbre — Wikipedia](https://en.wikipedia.org/wiki/Timbre)
