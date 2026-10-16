---
id: syn-harmonics-gibbs-timbre
title: Gibbs ripple and evolving timbre
level: intermediate
minutes: 3
summary: Gibbs ripple and evolving timbre.
sourceLesson: syn-harmonics
---

## Gibbs ripple

Adding up a finite number of harmonics never quite produces a perfect corner. A square wave built from odd harmonics overshoots each jump by about 9% of the jump size, in the limit of a large Fourier-series term count. A particular short finite sum differs slightly:

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

This is the **Gibbs phenomenon**. It matters later: a hard Fourier truncation of a square or saw shows this ripple even with every retained harmonic below Nyquist. Other smoothing windows and approximate oscillators can change the overshoot, so it is not a mandatory 18% peak for every anti-aliased implementation.

## Timbre is more than the static spectrum

The spectrum explains why waveforms differ, but real timbre also depends on how the spectrum **changes over time**. A piano's high harmonics die faster than its fundamental; a brass note gets brighter as it gets louder. That is why synths pair oscillators with filters, envelopes and modulation, which change the spectrum while the note plays. The DSP learning objectives ask you to describe a target sound in exactly these terms: pitch, spectrum, envelope and modulation.

## Key takeaways

- Limiting an ideal jump to finitely many Fourier terms creates ripple and overshoot.
- More terms narrow the overshoot region; allow peak headroom.
- Timbre includes changes over time as well as a steady magnitude spectrum.

## Further reading

- [Gibbs phenomenon — NIST DLMF](https://dlmf.nist.gov/6.16)
- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
