---
id: syn-harmonics-gibbs-timbre
title: Gibbs ripple and evolving timbre
level: intermediate
minutes: 3
summary: Gibbs ripple and evolving timbre.
sourceLesson: syn-harmonics
---

## Gibbs ripple

Adding up a finite number of harmonics never quite produces a perfect corner. A square wave built from odd harmonics overshoots each jump by about 9% of the jump size, in the limit of a large Fourier-series term count. A particular short finite sum differs slightly.

For an ideal square spanning minus one to plus one, a hard-truncated series with many odd harmonics therefore peaks near 1.179. That is roughly 1.4 dB above unity, so scaling by the intended flat level alone can clip the output. Measure the actual implementation and leave margin.

This is the **Gibbs phenomenon**. It matters later: a hard Fourier truncation of a square or saw shows this ripple even with every retained harmonic below Nyquist. Other smoothing windows and approximate oscillators can change the overshoot, so an overshoot of about 18% above the flat level is not mandatory for every anti-aliased implementation.

## Timbre is more than the static spectrum

The spectrum explains why waveforms differ, but real timbre also depends on how the spectrum **changes over time**. A piano's high harmonics die faster than its fundamental; a brass note gets brighter as it gets louder. That is why synths pair oscillators with filters, envelopes and modulation, which change the spectrum while the note plays. The DSP learning objectives ask you to describe a target sound in exactly these terms: pitch, spectrum, envelope and modulation.

## Key takeaways

- Limiting an ideal jump to finitely many Fourier terms creates ripple and overshoot.
- More terms narrow the overshoot region; allow peak headroom.
- Timbre includes changes over time as well as a steady magnitude spectrum.

## Further reading

- [Gibbs phenomenon — NIST DLMF](https://dlmf.nist.gov/6.16)
- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
