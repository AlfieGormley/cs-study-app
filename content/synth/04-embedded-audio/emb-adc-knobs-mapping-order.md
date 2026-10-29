---
id: emb-adc-knobs-mapping-order
sourceLesson: emb-adc-knobs
title: "Why smoothing order matters"
level: intermediate
minutes: 2
summary: "Smoothing hertz then taking a pitch ratio gives asymmetric upward and downward response."
---

A smoother closes a fraction of a gap, but **which kind of gap** matters. For a frequency control, a gap measured in hertz differs from one measured in octaves.

## Choose what should move evenly

If you map the knob exponentially to hertz and then smooth those hertz values, the smoother moves through equal fractions of the hertz gap. An upward jump covers more of its logarithmic frequency distance early; the reverse downward jump covers less. The imbalance depends on the frequency ratio, not simply whether the knob is near its top or bottom.

If you want matching progress in logarithmic frequency for upward and downward moves, smooth the normalised knob position **before** the exponential map, or smooth log-frequency. A one-pole then covers about 63% of the logarithmic distance after one time constant in either direction.

This describes a fixed-step model. It does not guarantee how every filter sweep will feel or sound: filter type, signal spectrum and the selected time constant matter. Hertz-domain smoothing may be intentional when that is the quantity you want to control.

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
