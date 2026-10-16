---
id: emb-adc-knobs-mapping-order
sourceLesson: emb-adc-knobs
title: "Why smoothing order matters"
level: intermediate
minutes: 2
summary: "Smoothing hertz then taking a pitch ratio gives asymmetric upward and downward response."
---

A normalised knob position spans zero to one. The earlier exponential map makes equal knob movements cover equal frequency ratios. This unit compares that map with a first-order smoother.

> [!tip] Map after smoothing
> Smooth the 0–1 control value, then map. If you smooth *after* an exponential map, the smoother works in hertz, which makes it lopsided in pitch: for a quarter-turn move (a ×5.6 frequency ratio), after one time constant a rise has covered about 79% of its musical distance but a fall only about 42%. Only the ratio matters, not where in the range you are, so logarithmic frequency progress is faster early in the upward direction than in the downward direction for this step model, and the larger the move the worse the imbalance. Smoothing the 0–1 value (or log-frequency) gives 63% in both directions.

## Key takeaways
- Smoothing hertz then taking a pitch ratio gives asymmetric upward and downward response.
- Smooth normalised position or log-frequency first when equal pitch progress is intended.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
