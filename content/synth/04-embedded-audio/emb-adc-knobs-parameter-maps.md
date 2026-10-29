---
id: emb-adc-knobs-parameter-maps
sourceLesson: emb-adc-knobs
title: "Map knob travel to useful values"
level: intermediate
minutes: 3
summary: "Linear maps give equal differences; exponential maps give equal ratios."
---

## Match the control's movement to the parameter

After scaling, a knob position usually runs from zero to one. **Mapping** turns that position into a useful parameter range. Choose both the range and the curve; the ADC does not choose them for you.

A **linear mapping** gives equal output differences for equal knob movements. It suits a normalised mix amount or pan position, with a separate pan law converting position to channel gains. Halfway along a linear 20 Hz–20 kHz frequency control is 10,010 Hz, leaving little travel for the low frequencies.

An **exponential mapping** gives equal positive output ratios for equal knob movements. Each octave is a doubling of frequency, so this often gives more useful control over a wide pitch or cutoff range. With the same endpoints, the middle is about 632 Hz: the ratio above the bottom equals the ratio below the top. These are numeric frequency relationships; the perceived cutoff sweep also depends on the signal and filter.

| Knob position | Linear frequency | Exponential frequency |
|---|---|---|
| Bottom | 20 Hz | 20 Hz |
| Middle | 10,010 Hz | About 632 Hz |
| Top | 20,000 Hz | 20,000 Hz |

For implementing a positive exponential range:

```formula reference
f = f_lo (f_hi / f_lo)^x
where
f: mapped frequency, in hertz (Hz)
f_lo: positive frequency at the bottom of the range, in hertz (Hz)
f_hi: positive frequency at the top of the range, in hertz (Hz)
x: normalised knob position, from zero to one, dimensionless
^x: raised to the power of the normalised knob position
Hz: hertz, cycles per second
In words: spread a positive frequency range so equal knob movements multiply frequency by equal ratios. The midpoint balances ratios, rather than hertz differences.
```

Exponential mapping also helps with envelope times spanning milliseconds to seconds. A decibel-based volume map gives equal amplitude ratios per step, without guaranteeing equal perceived loudness changes. Handle zero separately if the control must reach silence: a positive exponential range cannot include zero.

Test the curve and limits with the actual sound. More useful travel at one end is a design choice, not a universal law for every control.

## Key takeaways
- Linear maps give equal differences; exponential maps give equal ratios.
- Choose a curve and valid range for the parameter rather than assuming all controls feel alike.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
