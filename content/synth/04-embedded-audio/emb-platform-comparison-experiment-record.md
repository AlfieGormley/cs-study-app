---
id: emb-platform-comparison-experiment-record
sourceLesson: emb-platform-comparison
title: "Run a decisive test and record the choice"
level: advanced
minutes: 2
summary: "Choose the smallest isolated experiment that could change the platform decision."
---

## Step 6: run the smallest decisive experiment

Before committing, try the cheapest experiment that could change your mind:

- Run your oscillator and filter code offline on the computer and count operations per sample, to estimate CPU need.
- If one board is already available, do the roadmap's stage-6 exercises: flash and recover, read a knob and button, pass audio, measure load.
- Prototype the MIDI input circuit on a breadboard from the specification, at low voltage.
## Step 7: record the decision

Write a decision record (the project has `docs/decisions/` for this) containing:

1. The criteria and weights, with reasons.
2. The exact configurations, revisions and sources, with check dates.
3. The evidence table, including gaps and how they were closed.
4. The decision, the runner-up, and what would make you revisit it.
5. A parts list with electrical and interface checks, produced before purchase.

## Key takeaways
- Choose the smallest isolated experiment that could change the platform decision.
- Keep a reproducible decision record with remaining gaps and conditions for revisiting it.

## Further reading
- [Daisy Seed hardware page — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Teensy 4.1 — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Raspberry Pi 5 product brief — Raspberry Pi](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi audio boards configuration — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/configuration.adoc)
- [GPIO on Raspberry Pi — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/gpio-on-raspberry-pi.adoc)
- [Raspberry Pi models and their ports (Pi 5 lists no 3.5 mm jack) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/introduction.adoc)
