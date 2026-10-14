---
id: snd-prevent-aliasing
title: Prevent aliasing before it folds
level: intermediate
minutes: 3
summary: Choose input filtering, band-limited oscillators and oversampling where new high frequencies are created.
sourceLesson: snd-aliasing
---

## Preventing aliasing in a synth

There are two situations.

**1. Sampling a real analogue signal (an ADC).** Here an **anti-aliasing filter** removes content above Nyquist *before* it can fold. Every audio interface input has one. In a modern delta-sigma ADC, the converter samples many times faster than the final sample rate, so a simple analogue low-pass in front is enough, and a steep digital filter does the rest before the rate is reduced to the final rate.

**2. Generating a signal digitally (an oscillator).** There's no analogue signal to filter: the samples are computed directly. So the oscillator itself must only generate content below Nyquist. Established techniques, at a conceptual level:

- **Additive synthesis:** sum sines for each harmonic, stopping below Nyquist. Exact, but costly for low notes with hundreds of harmonics.
- **Band-limited wavetables:** precompute a single cycle with only the harmonics that fit, keeping several tables for different pitch ranges and picking one per note.
- **BLIT:** construct a band-limited impulse train and integrate it to obtain the desired waveform, taking care with DC and numerical drift.
- **BLEP** methods: replace each naive discontinuity with a band-limited step, often by adding a precomputed correction. PolyBLEP uses a cheap polynomial approximation to the step correction.
- **Oversampling:** run the oscillator at, say, 4× the output rate, low-pass filter digitally, then discard samples. Aliases still occur, but further up where harmonics are weaker, and the filter removes content outside the output passband before downsampling. Aliases already folded into that passband remain.

The roadmap suggests comparing a naive waveform with a library's band-limited version rather than inventing a technique. Stilson and Smith's paper in the further reading is the classic overview.

**Nonlinear processing aliases too.** Clipping, distortion and waveshaping create new harmonics. FM creates sidebands, which need not be harmonics. A hard clipper applied to a 5 kHz sine creates harmonics at 15, 25, 35 kHz and so on, and those above Nyquist fold back. Oversampling around the nonlinear stage is the standard remedy.

## Key takeaways

- ADC input filtering removes unwanted high frequencies before sampling or decimation.
- Digital oscillators need band-limited generation or a suitable correction technique.
- Nonlinear processing also generates above-Nyquist content. Oversampling helps, but it does not make naive waveforms alias-free.

## Further reading

- [Alias-Free Digital Synthesis of Classic Analog Waveforms — Stilson & Smith (CCRMA)](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Oversampling — Wikipedia](https://en.wikipedia.org/wiki/Oversampling)
- [Hard Sync Without Aliasing — Eli Brandt](https://www.cs.cmu.edu/~eli/papers/icmc01-hardsync.pdf)
