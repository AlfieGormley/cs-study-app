---
id: snd-peak-rms-dbfs
title: Peak, RMS and dBFS
level: intermediate
minutes: 4
summary: Measure digital level, compare crest factors and recognise different RMS meter conventions.
sourceLesson: snd-levels
---

## dBFS: decibels relative to full scale

**dBFS** measures a digital level relative to a defined full-scale reference. In a fixed PCM output format, that reference corresponds to the largest permitted sample level; floats can also hold values above it. With floats in ±1.0, full scale is 1.0, so the reference amplitude in the decibel formula is 1:

```formula reference
L = 20 log_10(|x| / 1.0)
where
L: the level, in decibels relative to full scale (dBFS)
log_10: the base-10 logarithm
x: a sample value (or a peak value), with ±1.0 as full scale; here 0.5
|x|: the absolute value of x, its size ignoring the sign
dBFS: decibels relative to nominal full scale; 0 dBFS is the fixed-output reference, even though internal floats can exceed it
In words: compare a value with full scale (1.0) on the decibel scale; anything smaller than full scale gets a negative number.
```

0 dBFS is the nominal sample-peak maximum at a fixed-format output. Smaller peaks read negative: a peak of 0.5 is −6 dBFS, a peak of 0.1 is −20 dBFS. A value of 2.0 would be +6 dBFS: fine inside a float pipeline, but it will clip at the converter.

> [!note] RMS and dBFS conventions differ
> For **peak** levels, dBFS is unambiguous. For **RMS** levels, conventions differ. AES17 (and related IEC and ITU standards) defines the RMS of a full-scale *sine* as 0 dBFS, so a full-scale square wave reads +3 dBFS. Other meters use the plain maths, where a full-scale sine reads −3 dBFS RMS. When comparing figures, check which convention a meter or datasheet uses. This lesson uses the plain maths.

## Peak, RMS and crest factor

Two measurements describe a signal's level:

- **Peak level:** the largest absolute sample value. It decides whether the digital samples exceed the fixed-format limit. Reconstructed analogue peaks can be higher between samples, which needs a separate true-peak check.
- **RMS (root mean square):** the square root of the average of the squared samples. It tracks the signal's power, and relates more closely to perceived loudness than peak does.

The name describes the recipe, read from right to left: square every sample, take the mean, then the square root.

```formula reference
RMS = √((1 / N) × Σ x[n]^2)
where
RMS: root mean square, the signal's "average size" in the power sense, in the same units as the samples
N: the number of samples measured (ideally a whole number of cycles)
Σ: sigma, "add up": sum the following over every sample n from the first to the Nth
x[n]: sample number n
n: the sample index
√: square root
In words: square each sample (making them all positive), average the squares, and take the square root to get back to the samples' units.
```

For a steady sine measured over whole cycles, RMS is below peak.

For a sine measured over whole cycles, RMS is about 71% of its peak. A sine peaking at 0.5 therefore has RMS about 0.354. This is a waveform-specific relationship, not a rule for arbitrary audio.

The ratio of peak to RMS is the **crest factor**, often given in dB:

```formula reference
CF = A_pk / RMS
CF_dB = 20 log_10(A_pk / RMS)
where
CF: the crest factor, a plain ratio (no unit)
CF_dB: the crest factor in decibels (dB)
dB: decibels
A_pk: the peak value, the largest absolute sample
RMS: the root-mean-square value
log_10: the base-10 logarithm
In words: the crest factor says how spiky a signal is: how far its peaks stand above its average level. For a sine it is about 1.414, or 3 dB.
```

| Waveform | Crest factor | In dB |
|---|---|---|
| Square | 1 | 0 |
| Sine | 1.414 (square root of 2) | 3.01 |
| Saw, triangle | 1.732 (square root of 3) | 4.77 |
| Music (varies widely) | often much higher | 12–20 is an example |

A square wave and a sine with the same peak don't sound equally loud: the square has 3 dB more RMS. Switching from sine to square at the same peak increases RMS by 3 dB and often sounds louder, but perceived loudness also depends on spectrum and listening level. Synths may compensate per waveform.

## Key takeaways

- Peak level tells you whether nominal full scale is exceeded; RMS measures average squared signal size.
- Crest factor is peak divided by RMS: a sine has about 3 dB, a square has 0 dB.
- RMS dBFS references differ between meters. Check conventions before comparing figures.

## Further reading

- [dBFS — Wikipedia](https://en.wikipedia.org/wiki/DBFS)
- [Crest factor — Wikipedia](https://en.wikipedia.org/wiki/Crest_factor)
