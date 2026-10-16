---
id: emb-platform-comparison-compare-gaps
sourceLesson: emb-platform-comparison
title: "Compare evidence and name the gaps"
level: advanced
minutes: 3
summary: "Clock rates and connector shapes do not prove the required performance or compatibility."
---

## Step 4: tabulate, and mark gaps honestly

| Criterion | A | B | C |
|---|---|---|---|
| Audio out | Line, 1 V RMS | Line + phones | 0–2 V RMS line |
| Audio in | Yes | Yes | No (DAC+) |
| Knob inputs | 12 ADC | 18 ADC | External ADC |
| Debug probe | ST-Link (SWD) | Not documented | Linux tools |
| Boot | Firmware | Firmware | Linux OS |
| Block default | 48 @ 48k | 128 @ 44.1k | Configurable |

Then list what the official sources **do not** tell you, and how you will find out:

- **Real CPU headroom for your synth.** Clock speeds are not workloads. Estimate from an offline prototype, then measure on the board (the real-time audio units).
- **Boot time** of the Linux configuration. Measure it.
- **Noise and output quality** in your studio. Listen and record.
- **Cost.** Prices change; record them on the day you buy, including shipping, headers, cables, a MIDI circuit and any probe.
- **Compatibility with your other equipment.** Check the Digitakt and audio interface manuals for ports and levels. A USB connector alone proves nothing: two USB *devices* cannot talk to each other directly; one side must be a host.
## Common mistakes

- **Comparing headline numbers.** 600 MHz versus 480 MHz says little about whether your synth fits; memory placement, library efficiency and your own code matter more.
- **Forgetting the rest of the system.** The board is a fraction of the build: MIDI circuit, power, connectors and instrument housing all count.
- **Trusting a forum post or an old video.** Use the official page for the exact revision, then verify on the bench.
- **Choosing for the final instrument only.** The project also values learning. A platform that hides the codec teaches less about integration but gets you to sound sooner. Decide which you want for version 1.

> [!note] Content absent pending reliable verification
> A project-specific wiring diagram, compatible bill of materials, measured voice count and end-to-end latency are not supplied here: the project has not selected its board, controls or exact interface, and no hardware bench measurements are available. Generic examples cannot reliably establish those facts. Confirm the configuration and measure it before treating any example as a build specification.

## Key takeaways
- Clock rates and connector shapes do not prove the required performance or compatibility.
- Close meaningful gaps with exact manuals and measurements.

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
