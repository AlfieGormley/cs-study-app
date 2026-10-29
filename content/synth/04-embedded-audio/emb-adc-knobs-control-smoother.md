---
id: emb-adc-knobs-control-smoother
sourceLesson: emb-adc-knobs
title: "Smooth knob readings"
level: intermediate
minutes: 3
summary: "A moving average needs a history buffer and introduces delay."
---

## Smooth the noise without making the knob sluggish

A still knob produces slightly different ADC readings. Smoothing reduces rapid variation, at the cost of delaying genuine movement. It does not replace good wiring or remove every kind of interference.

A **moving average** averages a short window of recent readings. Old readings gradually leave the window, so the result changes gradually. A longer window reduces uncorrelated, zero-mean noise more strongly but adds delay and needs more history storage. Correlated interference may remain. An eight-reading window has a group delay of 3.5 readings, or 3.5 ms at 1,000 readings per second.

A **one-pole low-pass smoother** keeps just its previous output. On each update it moves a chosen fraction of the remaining gap towards the new input. A small fraction means a slow, smooth response; a fraction of one means an immediate jump with no smoothing. With a fixed target and a fraction above zero and no greater than one, it does not overshoot.

> [!analogy] Real-world analogy: Approaching a doorway
> Imagine moving halfway from your current position to a doorway on every instruction.
>
> **How it maps:** A one-pole smoother closes a fixed fraction of the remaining gap on each update, so its early movements are larger than its later ones.
>
> **Where it stops:** Firmware works with discrete, finite-precision values and can round to a stop or to the target. The input can also move while the smoother follows it.

## Specify the response in time

An **exponential time constant** describes how quickly the gap closes: about 63.2% of a fixed step after one time constant and about 95% after three. It is not a time-to-arrival promise. In exact arithmetic a fraction strictly below one approaches the target without reaching it; finite precision changes the final numerical behaviour.

The per-update fraction depends on **both** the desired time constant and the update rate. Keeping the same fraction but doubling the update rate makes the response twice as fast in seconds. To keep the same response time at a higher rate, use a smaller fraction per update.

```formula reference
a = 1 − e^(−1 / (τr))
where
a: fraction of the remaining gap closed per update, dimensionless
τ: positive exponential time constant, in seconds (s)
r: update rate, in updates per second
e: Euler's number, about 2.71828
s: second, the unit of time
In words: choose the per-update movement from the desired response time and the update rate. Faster updates need smaller movements to preserve the same time constant.
```

A 10 ms time constant at 1,000 readings per second uses a fraction of about 0.0952. With that exponential coefficient, updates sample the corresponding exponential response; a time constant need not land exactly on an update. Initialise the retained output deliberately, and recompute the coefficient when the rate changes.

The libDaisy `AnalogControl` source uses a one-state smoother with a default slew setting of 0.002 s, but a different coefficient rule. Do not treat that library setting as this exact exponential time constant.

## Key takeaways
- A moving average needs a history buffer and introduces delay.
- A one-pole smoother retains state; its coefficient depends on update rate and time constant.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
- [AnalogControl implementation — libDaisy](https://raw.githubusercontent.com/electro-smith/libDaisy/master/src/hid/ctrl.cpp)
