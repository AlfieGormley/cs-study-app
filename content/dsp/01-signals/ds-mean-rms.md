---
id: ds-mean-rms
title: Mean, peak and RMS
level: basic
minutes: 3
summary: Measure a finite record’s offset and overall level with the correct units.
---

One number cannot describe every property of a signal. A sensor record can have a steady offset, a fluctuating component and occasional large excursions. **Record mean**, **peak magnitude** and **root mean square (RMS)** answer different questions. This lesson uses a non-empty finite record of real values; these are exact record descriptions, not estimates of an unknown infinite process.

## Mean and DC offset

The mean adds all samples and divides by the count. **DC** originally means direct current; in DSP a DC component is a constant offset. The record mean is the constant you subtract to centre that record at zero.

For `[1, 3]` volts the mean is 2 volts and the centred samples are `[-1, 1]` volts. The offset might be unwanted sensor bias, or it might be the actual quantity being measured. Do not remove it automatically. A short slice of a changing signal can have a nonzero mean without the underlying source having a permanent offset.

## Peak and RMS

Peak magnitude is the largest absolute sample value. RMS squares the samples, averages the squares and takes a square root. Squaring prevents positive and negative values cancelling. The final root restores the original units.

Mean zero does not mean no signal. A record alternating between −1 and +1 volt has zero mean, but its RMS is 1 volt. The signs cancel in the mean; they do not cancel when squared. Adding a constant offset increases this record’s RMS even though its fluctuations around its own mean stay the same.

> [!analogy] Real-world analogy: A commuter around home
> A commuter travels equal distances east and west of home. Their average signed position can be home even though they spend time far from it.
>
> **How it maps:** Mean uses signed positions, which can cancel. RMS measures distance from zero using squares, so opposite signs cannot erase the excursions. Peak records the farthest position reached.
>
> **Where it stops:** RMS is a particular squared-distance measure, not the average distance travelled or the length of the journey.

These reference expressions show how mean and RMS treat the same record differently:

```formula reference
μ = (Σ x[n]) / N
R = √((Σ x[n]^2) / N)
0 ≤ n ≤ N − 1
where
μ: record mean, in the signal’s units
R: record RMS, in the signal’s units
x: real-valued signal, in physical units or unitless
N: positive number of samples
n: integer sample index from zero through N − 1
Σ: add one term for each integer n in the stated range
√: non-negative square root
In words: Mean describes a record’s signed offset. RMS combines its offset and fluctuations without cancelling opposite signs, then returns the result in the original signal units.
```

## Choose the measurement for the decision

Use mean to examine offset, peak to check stored excursions against a limit, and RMS to describe overall squared level. Records with the same RMS can have different peaks, so an RMS limit alone does not guarantee freedom from clipping. Use the same measurement window when comparing records.

RMS has a connection to physical power only with a specified model, such as voltage across a fixed resistor. Squared temperature values are not automatically watts. Peak sample magnitude also need not equal the maximum of a continuous waveform between sampling instants.

## Key takeaways
- Mean describes offset; subtracting it changes the measured signal.
- Peak checks extremes; RMS includes both offset and fluctuations.
- Mean, peak and RMS retain the original signal units.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH2.PDF)
