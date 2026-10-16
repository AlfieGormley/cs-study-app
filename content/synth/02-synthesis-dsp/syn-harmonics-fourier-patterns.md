---
id: syn-harmonics-fourier-patterns
title: Fourier series and harmonic patterns
level: intermediate
minutes: 4
summary: Fourier series and harmonic patterns.
sourceLesson: syn-harmonics
---

A waveform’s harmonic amplitudes explain much of its steady timbre. This unit compares the ideal saw, square and triangle at the same fundamental frequency.

## The standard waveforms

| Wave | Harmonics present | Relative amplitude pattern |
|---|---|---|
| Sine | Fundamental only | No upper harmonics |
| Saw | All whole harmonics | Inverse harmonic number |
| Square | Odd harmonics | Inverse harmonic number |
| Triangle | Odd harmonics | Inverse square of harmonic number |

For waves swinging between −1 and +1, the standard series are:

```formula
ω = 2πf_0
x_saw(t) = (2 / π)
  × Σ (−1)^{(n + 1)} sin(nωt) / n
x_sq(t) = (4 / π) Σ sin(nωt) / n
x_tri(t) = (8 / π^2)
  × Σ (−1)^k sin(nωt) / n^2
where
ω: omega, the angular frequency of the fundamental, in radians per second: 2π radians per cycle times f_0 cycles per second
f_0: the fundamental frequency, in hertz (Hz)
π: pi, about 3.14159
x_saw(t), x_sq(t), x_tri(t): the ideal sawtooth, square and triangle series; at discontinuities the series takes the midpoint; finite truncations may overshoot the ideal extrema
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

The series scale factors give each ideal waveform’s fundamental amplitude:

```formula
A_saw = 2 / π ≈ 0.637
A_sq = 4 / π ≈ 1.273
A_tri = 8 / π^2 ≈ 0.811
where
A_saw, A_sq, A_tri: the fundamental’s peak amplitude for the ideal saw, square and triangle normalised to extrema of minus and plus one
π: pi, about 3.14159
≈: approximately equal to; values are rounded
In words: equal ideal peak extrema do not imply equal fundamental strengths.
```

 The alternating signs are phases; they shape the waveform but not the magnitude spectrum. The saw series shown ramps upward with its jump halfway through a cycle measured from the upward zero crossing. Its shift relative to the earlier phase-function saw changes phases, not harmonic magnitudes. The triangle here also starts at an upward zero crossing, rather than at the minimum used by the earlier phase-function triangle.

To compare harmonics by ear it helps to convert their relative amplitudes into decibels:

```formula
L = 20 log_10(A_n / A_1)
L = 20 log_10(1/2) ≈ −6.0 dB
L = 20 log_10(1/9) ≈ −19.1 dB
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
- **Square** has only odd harmonics with the same reciprocal-harmonic-number decay. Missing even harmonics give its hollow, woody, clarinet-like character.
- **Triangle** also has only odd harmonics, but they fall at the reciprocal of harmonic number squared, i.e. 12 dB per octave. The 3rd harmonic is 1/9 of the fundamental (−19 dB), so it sounds close to a sine.

## Key takeaways

- Fourier series describes periodic waves using DC and harmonics with magnitudes and phases.
- Saw harmonics decay by harmonic number; triangle harmonics decay faster than square harmonics.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Gibbs phenomenon — NIST DLMF](https://dlmf.nist.gov/6.16)
