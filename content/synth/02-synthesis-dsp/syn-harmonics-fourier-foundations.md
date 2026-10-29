---
id: syn-harmonics-fourier-foundations
title: Periodic sounds as Fourier series
level: intermediate
minutes: 3
summary: Periodic sounds as Fourier series.
sourceLesson: syn-harmonics
---

Play a sine, a triangle, a square and a sawtooth at the same pitch and loudness. Each sounds clearly different: the sine pure, the triangle soft, the square hollow, the saw buzzy and bright. Pitch and loudness are equal, so the difference is **timbre**, and for steady periodic tones timbre is largely set by the **spectrum**: which frequencies are present, and how strong each one is.

This lesson gives you the spectra of the standard waveforms and a way to verify them. Every later block (band-limiting, filters) is easier to reason about in these terms.

## Fourier series for ordinary periodic audio signals

A nonconstant periodic waveform has a fundamental frequency of one divided by its shortest repeating period, and, under the usual Fourier-series conditions for piecewise-smooth signals, it can be represented by a mean plus sinusoidal components at whole-number multiples of that repeat rate. At an ideal jump the series takes the midpoint of the one-sided limits.

Each component completes a whole number of cycles during the waveform’s repeat period. Its amplitude sets its contribution; its phase sets where that component starts. A constant mean is represented separately.

For example, a wave repeating every 10 milliseconds has a 100 Hz repeat rate. Its non-DC components lie on the 100, 200, 300 Hz grid and so on; some may have zero amplitude.

- DC is the mean value (zero for the centred waveforms here).
- The first harmonic is the **fundamental**; perceived pitch need not equal the strongest component.
- For this periodic sound, the second and higher harmonics are its **overtones**: components above the fundamental. “Harmonic” also includes the fundamental, which is not an overtone, and non-periodic sounds can have inharmonic overtones, so these words are not identical labels.
- Every component has its own amplitude and phase.

This is the **Fourier series**. Intuitively: a single sinusoid has one non-zero positive-frequency component, while a more complicated periodic waveform requires more components (and possibly a DC mean). The sharper the features of a waveform (corners, jumps), the more high harmonics it needs to build them.

The component *magnitudes* plotted against frequency form the **magnitude spectrum**: a row of spikes on the harmonic grid, each with a height.

## Key takeaways

- A periodic sound can be decomposed into a mean plus harmonics with individual phases and magnitudes.
- Its repeat rate sets the harmonic grid; the strongest component need not be the perceived pitch.

## Further reading

- [Fourier series — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Fourier_Series_FS_Relation.html)
- [Gibbs phenomenon — NIST DLMF](https://dlmf.nist.gov/6.16)
