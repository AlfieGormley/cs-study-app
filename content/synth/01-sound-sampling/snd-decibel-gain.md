---
id: snd-decibel-gain
title: Decibels and gain multipliers
level: intermediate
minutes: 3
summary: Choose amplitude or power decibels and convert a chain of gains to a sample multiplier.
sourceLesson: snd-levels
---

A synth that's too quiet is annoying. One that clips is broken: harsh, aliasing distortion every time a chord gets loud. Managing level is a constant job, from the first oscillator to the final converter, and decibels are the language for it.

## Why decibels

Level ratios in audio span an enormous range. An ideal signed 24-bit sample format has millions of steps between zero and full scale. Real converters have a higher analogue noise floor than that ideal resolution suggests. Ratios like that are unreadable as plain numbers, and our perception of loudness is roughly logarithmic anyway, so audio uses a logarithmic unit: the **decibel** (dB).

A decibel is always a **ratio** to something. There are two formulas, and mixing them up is the most common mistake. For quantities that measure power or energy:

```formula reference
L = 10 log_10(P_2 / P_1)
where
L: the level change, in decibels (dB); positive means louder
log_10: the base-10 logarithm, which answers "10 to what power gives this number?" (log_10(100) = 2)
P_1: the reference power (any unit, such as watts, W)
P_2: the power being compared, in the same unit as P_1; here twice P_1
dB: decibels, tenths of a bel
In words: ten times the logarithm of the power ratio gives decibels, so doubling the power is about +3 dB.
```

For amplitudes (sample values, voltages, sound pressures):

```formula reference
L = 20 log_10(A_2 / A_1)
where
L: the level change, in decibels (dB)
log_10: the base-10 logarithm
A_1: the reference amplitude (a sample value, or volts, V)
A_2: the amplitude being compared, in the same unit; here twice A_1
dB: decibels
In words: twenty times the logarithm of the amplitude ratio gives decibels, so doubling an amplitude is about +6 dB.
```

Why the different factors? At unchanged impedance, power grows with squared voltage amplitude.

At the same impedance, doubling voltage quadruples power. The amplitude and power decibel rules therefore describe the same physical change when applied to the appropriate quantities.

Under that condition both formulas give the **same** dB value for the same change; you just use the one matching the quantity you have. Samples, voltages and pressures are **amplitudes**, so use the amplitude rule when comparing their magnitudes.

Going back from decibels to a multiplier undoes the logarithm:

```formula reference
g = 10^(L / 20)
where
g: the amplitude multiplier (gain factor) to apply to the samples; no unit
L: the level change, in decibels (dB); here −6 dB
10^x: 10 raised to the power x, the inverse of log_10
In words: divide the decibels by 20 and raise 10 to that power; −6 dB means multiply the samples by about 0.5.
```

Useful reference landmarks: **doubling an amplitude adds about 6 dB**, **×10 adds 20 dB**, and **×1.414 (the square root of 2) adds about 3 dB**. In power terms, doubling power is +3 dB. Gains in dB **add** where the ratios multiply:

A −6 dB stage followed by a −12 dB stage gives −18 dB overall, about one eighth of the original sample amplitude. Add the decibel changes; multiply the corresponding linear gains.

## Key takeaways

- Use twenty times the log for amplitude ratios and ten times the log for power ratios.
- Doubling amplitude adds about 6 dB; doubling power adds about 3 dB.
- Serial gains add in decibels and multiply as linear factors.

## Further reading

- [Decibel — Wikipedia](https://en.wikipedia.org/wiki/Decibel)
- [Decibels and amplitude ratios — UNSW](https://www.phys.unsw.edu.au/jw/dB.html)
