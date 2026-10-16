---
id: aud-crossovers-linkwitz-riley
title: Why Linkwitz–Riley can sum flat
level: advanced
minutes: 5
summary: Cascaded Butterworth sections give each Linkwitz–Riley output half amplitude at crossover.
sourceLesson: aud-crossovers
---

## Linkwitz–Riley summation

### Linkwitz–Riley

Siegfried Linkwitz and Russ Riley's fix (1976) was to cascade **two Butterworth filters** of the same order on each side. Each output is then **−6 dB** at the crossover, half the voltage, and the two halves add to exactly 0 dB:

```formula
A_LR = A_BW^2
A_LR = 0.707 × 0.707 ≈ 0.5
A_sum = 0.5 + 0.5 = 1
L_sum = 20 log_10(1) = 0 dB
where
A_LR: the size of one Linkwitz–Riley output at the crossover, as a fraction of the input (no unit)
A_BW: the size of one Butterworth section's output at the crossover: 0.707 (−3 dB)
A_sum: the size of the summed output (in-phase outputs), as a fraction of the input
L_sum: the summed level, in decibels (dB)
log_10: the base-10 logarithm
dB: decibel, the unit of level ratio
In words: putting two −3 dB filters in a row gives −6 dB (half the voltage), and two halves added in step make exactly the original level.
```

- **LR2** (two first-order sections): 12 dB/octave, outputs 180° apart, so one driver is reversed in polarity. Sums flat.
- **LR4** (two second-order Butterworths): 24 dB/octave. At the crossover the low-pass is at −180° and the high-pass at +180°, which is a **360° difference: the outputs are in phase at every frequency**. They sum to a flat magnitude, and the total behaves as an **all-pass** filter: flat amplitude with smoothly changing phase.

Why does LR4 sum flat at *every* frequency, not just at the crossover? Write each output as a transfer function, using the same normalised frequency variable as the first-order example, and compare the sizes of the top and bottom of the sum:

```formula
D = s^2 + √(2)s + 1
LP = 1 / D^2
HP = s^4 / D^2
LP + HP = (1 + s^4) / D^2
s = ju
|1 + s^4| = 1 + u^4
|D|^2 = (1 − u^2)^2 + 2u^2
|D|^2 = 1 + u^4
|LP + HP| = (1 + u^4) / (1 + u^4) = 1
where
D: the denominator (bottom line) of a second-order Butterworth filter; no unit
s: the normalised complex frequency (the Laplace variable); for a steady sine it equals j × u
LP: the LR4 low-pass output as a fraction of the input (two Butterworth low-passes in a row, so D is squared)
HP: the LR4 high-pass output as a fraction of the input
j: the imaginary unit, the square root of −1; it keeps track of phase. j^4 = 1, so s^4 = u^4
u: normalised frequency, the normalised frequency: the actual frequency divided by the crossover frequency (no unit); u = 1 at the crossover
√: square root
| |: the magnitude (size) of a complex number, ignoring its phase
In words: the top and the bottom of the summed transfer function always have the same size, so the sum's size is exactly 1 (0 dB) at every frequency; only its phase changes.
```

The denominator polynomial has odd powers that the numerator lacks, so they are not identical polynomials and the sum’s phase still rotates. That's exactly what an all-pass filter is.

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
