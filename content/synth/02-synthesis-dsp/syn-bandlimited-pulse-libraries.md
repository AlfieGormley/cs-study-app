---
id: syn-bandlimited-pulse-libraries
title: Pulse corrections and library oscillators
level: intermediate
minutes: 4
summary: Pulse corrections and library oscillators.
sourceLesson: syn-bandlimited
---

The saw's jump is downwards (+1 to −1), so the correction is *subtracted*. A square has a rising jump at phase 0 and a falling one at the oscillator pulse width w, so it needs two corrections:

```formula
y = s + B(p) − B((p − w) mod 1)
where
y: the corrected pulse output sample
s: the naive pulse: +1 while p < w, otherwise −1
p: the phase, from 0 up to 1
w: the oscillator pulse width, as a fraction of the cycle (0.5 for a square)
B(x): the signed PolyBLEP step-correction function at the wrapped phase x, using the same fixed positive increment for both edges
x: the function’s dummy phase argument, from zero inclusive to one exclusive
mod: modulo, the remainder after division; (p − w) mod 1 is the phase measured from the falling edge, wrapped into 0 to 1
In words: add a correction at the rising edge and subtract one at the falling edge, each measured from its own jump.
```

This is a Python fragment using the preceding unit’s `poly_blep` function. Supply a phase, a fixed oscillator pulse width strictly between zero and one, and a positive increment below half a cycle per sample. Extremely narrow pulses and moving edges need additional validation:

```python
y = 1.0 if p < w else -1.0

# Rising edge at the start of each cycle.
y += poly_blep(p, dt)

# Falling edge measured from the duty point.
y -= poly_blep((p - w) % 1.0, dt)
```

The same fixed-frequency FFT check, at oscillator pulse widths 0.5 and 0.3, gave −55.4 dB worst off-harmonic bin below 10 kHz for the corrected version (naive: −29.8 and −28.7 dB respectively). Remember that a pulse with a width other than 0.5 also has a DC offset (a non-zero average), which you may want to remove:

```formula
DC = w(+1) + (1 − w) × (−1) = 2w − 1
DC = 2 × 0.3 − 1 = −0.4
where
DC: the average value of the pulse over one cycle
w: the oscillator pulse width, the fraction of the cycle spent at +1; the rest, 1 − w, is spent at −1
In words: the average is the time-weighted mix of +1 and −1, which is zero only for a square (w = 0.5).
```

Triangle waves have corners, not jumps. They can be corrected with a band-limited *ramp* (BLAMP), or made by integrating a PolyBLEP square with a leaky integrator, which is what DaisySP's `WAVE_POLYBLEP_TRI` does.

## Using a library

You don't need to invent any of this. Source revisions checked 2026-10-16: DaisySP 2c72eaf9eac5 and PJRC Audio 3039be2773e8. These are software-library observations, not a board-revision compatibility claim; confirm your installed library before copying names:

- **DaisySP** `Oscillator` offers naive waveforms plus `WAVE_POLYBLEP_SAW`, `WAVE_POLYBLEP_SQUARE` and `WAVE_POLYBLEP_TRI`.
- **Teensy Audio Library** `AudioSynthWaveform` offers `WAVEFORM_BANDLIMIT_SAWTOOTH`, `WAVEFORM_BANDLIMIT_SAWTOOTH_REVERSE`, `WAVEFORM_BANDLIMIT_SQUARE` and `WAVEFORM_BANDLIMIT_PULSE` alongside the naive ones. Its source (`synth_waveform.cpp`, class `BandLimitedWaveform`) inserts a precomputed band-limited step from a lookup table at each edge, interpolated to the edge's fractional position and spread across a window of about 32 samples (16 either side of the edge): a table-based BLEP approach, not PolyBLEP.

The roadmap exercise is exactly this lesson's experiment: generate naive and band-limited versions at a high pitch, run them through the FFT analysis, and listen to a slow upward sweep of each.

The fixed-note test also works with the actual checked DaisySP oscillator source compiled on the host: the naive saw’s strongest off-harmonic bin below 10 kHz was about −29.83 dB relative to its fundamental, versus −55.45 dB for its PolyBLEP saw. The tenth-harmonic droop was about −1.95 dB. These measurements agree closely with the offline Python implementation; they do not measure a board’s real-time capacity, output circuit or behaviour under rapidly changing pitch.

## Choosing a method

| Method | CPU | Memory | Notes |
|---|---|---|---|
| Additive | high | low | exact; costly for low notes |
| Mipmapped tables | low | medium | any waveform |
| Oversampling | high | low | needs a good decimator |
| PolyBLEP | low | no correction table | some top-end droop |
| minBLEP | medium | small table | better suppression |

For a first subtractive voice on a microcontroller, PolyBLEP is the usual pragmatic choice.

## Key takeaways

- Pulse waves need opposite corrections at rising and falling edges.
- Non-half duty cycles have a non-zero mean.
- Inspect the exact library revision and compare its output with the naive oscillator.

## Further reading

- [Oscillator implementation — DaisySP](https://raw.githubusercontent.com/electro-smith/DaisySP/2c72eaf9eac5fc0dca1919d65d606da907832618/Source/Synthesis/oscillator.cpp)
- [Waveform implementation — PJRC](https://raw.githubusercontent.com/PaulStoffregen/Audio/3039be2773e86daf1f381a1e8bdc1e6a55ed11f1/synth_waveform.cpp)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
