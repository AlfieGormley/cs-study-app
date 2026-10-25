---
id: ds-decibels
title: Decibels need a reference
level: basic
minutes: 5
summary: Choose amplitude or power ratios and handle zero deliberately.
---

A **decibel (dB)** expresses a ratio on a logarithmic scale. It makes large ratios manageable and turns successive multiplicative gains into additive level changes. A bare decibel value is incomplete unless you know what is compared: power, amplitude, or a level relative to a named reference.

Zero decibels means equal numerator and reference, not silence. Negative decibels mean the numerator is smaller than its reference. They do not mean a negative amplitude or negative physical power.

## Power and amplitude are different

For positive powers, use ten times the base-ten logarithm. The **logarithm** asks which power of ten produces the ratio: a ratio of 100 has logarithm 2.

```formula
L_P = 10 log_10(P / P_ref)
L_P = 10 log_10(4) ≈ 6.021 dB
where
L_P: power level relative to the reference, in decibels (dB)
P: positive measured power, in the same units as P_ref
P_ref: positive reference power
log_10: base-ten logarithm of a positive unitless ratio
dB: decibel, one tenth of a bel, the logarithmic ratio unit
≈: approximately equal, rounded here
In words: Four times the reference power is about six decibels above it.
```

For positive amplitude magnitudes of the same kind, the conventional amplitude-ratio expression uses twenty. When physical power is proportional to amplitude squared with the same proportionality factor, it agrees with the power expression. Comparing voltages across different resistances does not meet that assumption.

```formula
L_A = 20 log_10(A / A_ref)
L_A = 20 log_10(0.5) ≈ −6.021 dB
where
L_A: amplitude level relative to the reference, in decibels (dB)
A: positive measured amplitude magnitude, such as RMS voltage
A_ref: positive reference amplitude of the same kind and unit as A
log_10: base-ten logarithm of a positive unitless ratio
dB: decibel, the logarithmic ratio unit
≈: approximately equal, rounded here
In words: Half the reference amplitude is about six decibels below it; the factor twenty accounts for squared amplitude in the corresponding power ratio.
```

Do not compare peak amplitude to an RMS reference without saying so. A reference of 1 volt RMS produces a different statement from a reference of 1 unitless peak amplitude, even if both ratios happen to have the same number.

## Zero and digital full scale

The logarithm of zero has no finite real value. As a positive amplitude approaches zero, its decibel level decreases without a finite lower limit. For a display, report silence separately or choose and label a display floor. A floor is a display policy, not a measured nonzero signal.

**dBFS** means decibels relative to digital full scale. Metering conventions differ, especially for RMS sine references. In this course’s simple unitless peak meter, full-scale peak magnitude is 1 and the amplitude reference is that same value. A peak of 0.5 is therefore about −6.021 dB relative to full-scale peak. This definition does not assert a universal sine-RMS convention.

This complete example implements that particular peak reference. `math.log10` takes a positive ratio. It handles zero explicitly and rejects negative magnitudes rather than hiding them with an absolute value.

```python
import math
def peak_db(a):
    if a < 0:
        raise ValueError('negative input')
    if a == 0:
        return -math.inf
    return 20 * math.log10(a / 1.0)
print(round(peak_db(0.5), 3))
print(peak_db(0.0))
# -6.021
# -inf
```

Write the ratio and reference in measurement reports so another person can reproduce the level.

## Key takeaways
- Use ten for power ratios and twenty for amplitude ratios under the stated interpretation.
- Name the reference and whether amplitude means peak or RMS.
- Zero needs deliberate handling; a display floor is a policy.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH14.PDF)
- [Analog Devices AN-938: full-scale and RMS conventions](https://www.analog.com/en/resources/app-notes/2020/11/30/17/36/an-938.html)
