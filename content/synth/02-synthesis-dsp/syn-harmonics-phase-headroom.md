---
id: syn-harmonics-phase-headroom
title: Phase alignment and peak headroom
level: intermediate
minutes: 3
summary: Phase alignment and peak headroom.
sourceLesson: syn-harmonics
---

## Equal magnitudes can hide different shapes

Two waves can have identical magnitude spectra but different shapes. Build a 39-harmonic saw-like tone twice: once with all harmonics in sine phase, once all in cosine phase.

```python
import numpy as np

fs, f0 = 48000, 100
t = np.arange(fs) / fs

def build(phase):
    x = np.zeros(fs)
    for n in range(1, 40):   # 39 harmonics
        # Each harmonic has inverse-number
        # gain.
        x += np.sin(2*np.pi*n*f0*t
                    + phase) / n
    return x


# Same amplitudes; change only starting
# phase.
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
ΔL = 20 log_10(P_2 / P_1)
ΔL = 20 log_10(4.25 / 1.81) ≈ 7.4 dB
where
ΔL: delta L, the difference in peak level, in decibels (dB)
P_1: the peak of the sine-phase version, 1.81
P_2: the peak of the cosine-phase version, 4.25
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to
In words: lining up the harmonics' crests raised the peak by about 7.4 dB without changing any harmonic's amplitude.
```

The experiment proves equal harmonic magnitudes, not equal perception. Human studies of harmonic complexes show that phase differences can be audible, with sensitivity depending on harmonic resolution, fundamental frequency and listening conditions. Listen if timbre matters; do not use a magnitude FFT as proof that two tones must sound identical. Your **headroom** does not care what it sounds like: the peak is what clips. Filters change phases, which is one reason a filtered signal can peak higher than its input.

For a changing note, the harmonic levels and phases can evolve during the attack and decay. One static magnitude spectrum cannot describe all that articulation; the next unit returns to this broader meaning of timbre.

## Key takeaways

- Equal magnitude spectra can have different time-domain peaks.
- Phase changes can consume headroom even when the steady-state RMS is unchanged.

## Further reading

- [FFT definitions and normalisation — NumPy](https://numpy.org/doc/stable/reference/routines.fft.html)
- [mdft](https://ccrma.stanford.edu/~jos/mdft/)
- [Phase discrimination in harmonic complexes — Drennan and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC2536810/)
