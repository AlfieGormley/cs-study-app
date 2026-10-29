---
id: aud-crossovers-linkwitz-riley
title: Why Linkwitz–Riley can sum flat
level: advanced
minutes: 4
summary: Cascaded Butterworth sections give each Linkwitz–Riley output half amplitude at crossover.
sourceLesson: aud-crossovers
---

## Linkwitz–Riley summation

### Linkwitz–Riley

Siegfried Linkwitz and Russ Riley's fix (1976) was to cascade **two Butterworth filters** of the same order on each side. Two −3 dB stages in a row give **−6 dB** at the crossover: half the voltage. When the two outputs are in step, the two halves add to exactly the original level: 0 dB, no bump and no notch.

- **LR2** (two first-order sections): 12 dB/octave, outputs 180° apart, so one driver is reversed in polarity. Sums flat.
- **LR4** (two second-order Butterworths): 24 dB/octave. At the crossover the low-pass is at −180° and the high-pass at +180°, which is a **360° difference: the outputs are in phase at every frequency**. They sum to a flat magnitude, and the total behaves as an **all-pass** filter: flat amplitude with smoothly changing phase.

Why does LR4 sum flat at *every* frequency, not just at the crossover? Because the outputs stay in phase throughout, and their sizes always add to exactly one. Writing the two outputs as transfer functions shows that the top and bottom of the summed fraction always have equal size, while their phases differ; the Rane and Linkwitz notes in Further reading work through it. The flat sum is not "doing nothing", though: the phase of the combined output still rotates through 360° across the crossover region, which delays the lower frequencies slightly relative to the higher ones. That is exactly what an all-pass filter is.

| Crossover | Each output at crossover | Sum at crossover |
|---|---|---|
| BW2, one driver inverted | −3 dB | +3 dB peak |
| LR2, one driver inverted | −6 dB | 0 dB |
| LR4 | −6 dB | 0 dB, in phase |

LR4 is a very common choice in active and DSP crossovers, including PA processors.

## Key takeaways
- Cascaded Butterworth sections give each Linkwitz–Riley output half amplitude at crossover.
- The correctly aligned LR4 sum has flat magnitude and varying phase.
- Ideal mathematical summation assumes suitable driver responses and equal path lengths.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
