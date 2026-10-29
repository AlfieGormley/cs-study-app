---
id: syn-bandlimited-pulse-libraries
title: Pulse corrections and library oscillators
level: intermediate
minutes: 4
summary: Pulse corrections and library oscillators.
sourceLesson: syn-bandlimited
---

The saw's jump is downwards (+1 to −1), so the correction is *subtracted*. A square has a rising jump at phase 0 and a falling one at the oscillator pulse width `w`, so it needs two corrections.

This is a Python fragment using the preceding unit’s `poly_blep` function. Supply phase `p`, a fixed oscillator pulse width `w` strictly between zero and one, and a positive increment `dt` below half a cycle per sample. Extremely narrow pulses and moving edges need additional validation:

```python
y = 1.0 if p < w else -1.0

# Rising edge at the start of each cycle.
y += poly_blep(p, dt)

# Falling edge measured from the duty point.
y -= poly_blep((p - w) % 1.0, dt)
```

The same fixed-frequency FFT check, at oscillator pulse widths 0.5 and 0.3, gave −55.4 dB worst off-harmonic bin below 10 kHz for the corrected version (naive: −29.8 and −28.7 dB respectively). Remember that a pulse with a width other than 0.5 also has a DC offset (a non-zero average), which you may want to remove.

A pulse held high for less than half the cycle has a negative mean; held high for more than half, it has a positive mean. At a high fraction of 0.3 its mean is −0.4. Remove unwanted DC with a suitable blocker, allowing for its effect on low frequencies.

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
| Additive | high | low | exact fixed-frequency sum; costly for low notes |
| Mipmapped tables | low | medium | any waveform |
| Oversampling | high | low | needs a good decimator |
| PolyBLEP | low | no correction table | some top-end droop |
| minBLEP | medium | small table | longer corrections can improve suppression |

For a first subtractive voice on a microcontroller, PolyBLEP is the usual pragmatic choice.

## Key takeaways

- Pulse waves need opposite corrections at rising and falling edges.
- Non-half duty cycles have a non-zero mean.
- Inspect the exact library revision and compare its output with the naive oscillator.

## Further reading

- [Oscillator implementation — DaisySP](https://raw.githubusercontent.com/electro-smith/DaisySP/2c72eaf9eac5fc0dca1919d65d606da907832618/Source/Synthesis/oscillator.cpp)
- [Waveform implementation — PJRC](https://raw.githubusercontent.com/PaulStoffregen/Audio/3039be2773e86daf1f381a1e8bdc1e6a55ed11f1/synth_waveform.cpp)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
