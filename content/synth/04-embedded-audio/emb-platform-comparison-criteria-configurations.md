---
id: emb-platform-comparison-criteria-configurations
sourceLesson: emb-platform-comparison
title: "Define criteria and complete candidates"
level: advanced
minutes: 2
summary: "Write pass/fail requirements and weighted priorities before comparing products."
---

The diy-synth project deliberately leaves the board open. This lesson does not choose one. It gives you a repeatable method for comparing candidates, demonstrates it with facts taken only from the manufacturers' current documentation, and shows where the evidence runs out.

> [!warning] Re-verify before buying
> Every product fact below was checked on **2026-10-16** against the named official source and model or revision. Boards change revision, codecs get substituted (the Daisy Seed has had three), and products move between manufacturers. Treat this lesson as a snapshot. Re-check each fact against the current official page before you spend money, and record your own check date.

## Step 1: write the criteria before looking at boards

Looking at spec sheets first makes the biggest numbers feel important. Start from the project instead. The project brief and the hardware-options checklist give these criteria:

**Must-haves** (pass/fail):

- Audio output suitable for an audio interface's line input.
- A control connection an external device (the Digitakt) can drive.
- Enough inputs for the planned buttons and knobs.
- A screen that identifies the selected waveform type, as the project brief requires; include its bus, pins, power and foreground update budget.
- A C++ toolchain that works on the development computer.
- A documented way to flash, and to recover a broken board.
- Low-voltage power only.

**Weighted criteria** (scored):

- Beginner documentation and working audio examples.
- Debugging workflow and extra equipment needed.
- CPU, RAM and flash headroom for the intended synth.
- Total prototype cost: board plus audio board, MIDI circuit, power, cables, tools.
- Soldering and construction effort.
- Availability, revision stability, maintenance.
- Fit with the learning goals (C++, DSP, embedded).

Decide the weights *before* scoring, and write down why.
## Step 2: define exact configurations

"Teensy" is not a configuration. Compare complete, buildable systems:

| Label | Configuration |
|---|---|
| A | Daisy Seed, Rev 7 |
| B | Teensy 4.1 + audio adaptor Rev D2 |
| C | Raspberry Pi 5 + Raspberry Pi DAC+ |

Each still needs a DIN MIDI interface circuit (or another agreed control link), power, cables, and possibly a debug probe. List those per configuration; they are part of the cost and the build effort. (Pi alternatives include the DAC Pro or the Codec Zero, which differ in outputs and inputs.)

## Key takeaways
- Write pass/fail requirements and weighted priorities before comparing products.
- Include the waveform display and every supporting part in the configuration.

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
