---
id: ds-decibels
title: Decibels need a reference
level: basic
minutes: 4
summary: Interpret level changes by naming the measured quantity and its reference.
---

A **decibel (dB)** expresses a ratio on a logarithmic scale. It makes large ratios manageable and turns successive multiplicative gains into additive level changes. A bare decibel value is incomplete unless you know what is compared: power, amplitude, or a level relative to a named reference.

Zero decibels means equal numerator and reference, not silence. Negative decibels mean the numerator is smaller than its reference. They do not mean a negative amplitude or negative physical power.

## Power and amplitude are different

For positive powers, a tenfold increase is +10 dB and a tenfold decrease is −10 dB. For amplitude magnitudes such as voltage, a tenfold increase is +20 dB. Do not apply an amplitude rule to a power ratio.

The different scales agree when power is proportional to amplitude squared with the same proportionality factor. For example, halving an RMS voltage across the same resistance quarters the power; both describe about a 6 dB decrease. Across different resistances, the voltage ratio alone does not establish the power ratio.

The reference expressions use a **logarithm**, which asks which power of ten produces a ratio. They are useful for converting a measured ratio, rather than memorising separate answers for every possible change.

```formula reference
L_P = 10 log_10(P / P_ref)
where
L_P: power level relative to the reference, in decibels (dB)
P: positive measured power, in the same units as P_ref
P_ref: positive reference power
log_10: base-ten logarithm of a positive unitless ratio
dB: decibel, one tenth of a bel, the logarithmic ratio unit
In words: A tenfold power increase raises the level by ten decibels. Equal power and reference give zero decibels; a smaller positive power gives a negative level.
```

For positive amplitude magnitudes of the same kind, the conventional amplitude-ratio expression uses twenty:

```formula reference
L_A = 20 log_10(A / A_ref)
where
L_A: amplitude level relative to the reference, in decibels (dB)
A: positive measured amplitude magnitude, such as RMS voltage
A_ref: positive reference amplitude of the same kind and unit as A
log_10: base-ten logarithm of a positive unitless ratio
dB: decibel, the logarithmic ratio unit
In words: A tenfold amplitude increase raises the level by twenty decibels. Halving amplitude lowers it by about six decibels; this agrees with the power change when power follows amplitude squared with the same proportionality factor.
```

Successive gains add as decibel changes: a 6 dB increase followed by a 6 dB decrease returns to the original level if the stages apply those gains without clipping or other changes. That does not mean adding the decibel readings of two separate signals predicts their mixed level; their timing and phase also matter.

Do not compare peak amplitude to an RMS reference without saying so. A reference of 1 volt RMS produces a different statement from a reference of 1 unitless peak amplitude, even if both ratios happen to have the same number.

## Zero and digital full scale

The logarithm of zero has no finite real value. As a positive amplitude approaches zero, its decibel level decreases without a finite lower limit. For a display, report silence separately or choose and label a display floor. A floor is a display policy, not a measured nonzero signal.

**dBFS** means decibels relative to digital full scale. Metering conventions differ, especially for RMS sine references. In this course’s simple unitless peak meter, full-scale peak magnitude is 1 and the amplitude reference is that same value. A peak of 0.5 is about −6 dB relative to full-scale peak. This definition does not assert a universal sine-RMS convention.

Write the ratio and reference in measurement reports so another person can reproduce the level.

## Key takeaways
- Use ten for power ratios and twenty for amplitude ratios under the stated interpretation.
- Name the reference and whether amplitude means peak or RMS.
- Zero needs deliberate handling; a display floor is a policy.

## Further reading
- [Steven W. Smith: power and amplitude decibels](https://www.dspguide.com/CH14.PDF)
- [Analog Devices AN-938: full-scale and RMS conventions](https://www.analog.com/media/en/technical-documentation/app-notes/an-938.pdf)
