---
id: emb-adc-knobs-resolution-noise
sourceLesson: emb-adc-knobs
title: "ADC codes and usable resolution"
level: intermediate
minutes: 3
summary: "An ideal converter has a power-of-two number of codes and a defined voltage per code."
---

A knob is usually a potentiometer used as a voltage divider. An **ADC** samples its voltage and returns an integer **code**. That code is a measurement with finite resolution and noise, not a perfect statement of the knob position.

## More codes mean finer steps

**Resolution** is the number of bits in a reading. Each extra bit doubles the number of possible codes and halves the ideal voltage spacing over the same input range. A 12-bit ADC has 4,096 codes, numbered 0–4,095. With an ideal 0–3.3 V span, neighbouring code levels are about 0.81 mV apart. This spacing is one **LSB**, the least significant bit's voltage value.

The **reference voltage** sets the conversion scale. Check the documented analogue input range independently of any digital pin's voltage tolerance: the Daisy Seed and Teensy 4.1 analogue inputs discussed here use 0–3.3 V.

This reference is useful when comparing a measured noise voltage with code spacing:

```formula reference
LSB = V_span / 2^N
where
LSB: ideal spacing between adjacent code levels, in volts (V)
V_span: full input voltage span for the specified conversion range, in volts (V)
N: ADC resolution, in bits
2^N: two raised to the number of bits, giving the number of codes
V: volt, the unit of voltage
In words: divide the input voltage span among all available codes. More bits give smaller ideal steps, but do not make the input or reference less noisy.
```

## Resolution is not accuracy

With the knob still, wiring pick-up, reference noise and converter noise can make the code wander. Increasing the configured bit count can expose smaller changes without making them useful measurements. Measure the real circuit before treating nominal resolution as accuracy or noise-free resolution.

PJRC documents 10-bit default readings on Teensy 4.1, 12-bit hardware capability, and normally only up to 10 usable bits because of noise. Electro-Smith describes Daisy's ADC as up to 16 bits; its `GetFloat()` API scales the reading to 0–1. A float return type does not add analogue accuracy.

**Sample rate** is how often a conversion happens, distinct from bit depth. A few hundred to a thousand readings per second is a common starting range for hand-operated knobs; measure responsiveness and processing cost. Audio converters instead use their supported audio rates, such as 44.1 or 48 kHz. Smooth and map control readings before using them; the next units explain why.

## Key takeaways
- An ideal converter has a power-of-two number of codes and a defined voltage per code.
- Nominal resolution does not establish accuracy or noise-free resolution.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
