---
id: emb-codecs-i2s-converter-revisions
sourceLesson: emb-codecs-i2s
title: "Know the converter on your board"
level: intermediate
minutes: 2
summary: "A hardware audio codec includes conversion in both directions."
---

Your oscillator produces a stream of numbers. Somewhere between that stream and the cable into your audio interface, the numbers must become a smoothly varying voltage at the right level. This lesson follows that path: the converter chip, the digital link that feeds it, the memory trick that keeps it fed, and the analogue stage at the end.

## DAC, ADC and codec

- A **DAC** (digital-to-analogue converter) turns sample values into a voltage.
- An **ADC** does the reverse (the knob-reading units used the MCU's own ADC for knobs).
- An audio **codec** (coder/decoder) is one chip containing ADC and DAC functions, often stereo, the digital filters that go with them, and often extras such as volume control, a headphone amplifier and input selection.

Many MCUs have an on-chip DAC too. The Daisy Seed exposes two 12-bit DAC outputs; they are useful for control voltages or simple signals, but the audio path uses the separate codec, which is designed for low noise and distortion.

Codecs on the boards in this course (checked 2026-10-16):

| Board | Converter | Control |
|---|---|---|
| Daisy Seed Rev 7 | TI PCM3060 | Pins (no I2C) |
| Daisy Seed Rev 5 | WM8731 | I2C |
| Teensy audio adaptor Rev D/D2 | SGTL5000 | I2C |
| Pi DAC+ HAT | TI PCM5122 | I2C |

The Daisy row shows why the project brief insists on naming revisions: Rev 4 used AK4556, Rev 5 used WM8731 and Rev 7 uses PCM3060. The datasheet says the revision check grounds PD3 on Rev 5 and PD5 on Rev 7; the fetched libDaisy distinguishes Rev 7 and shares its audio setup with the Rev 4-compatible configuration. Use a library version that supports the actual board, rather than assuming every historic firmware image does.

## Key takeaways
- A hardware audio codec includes conversion in both directions.
- Record board revision, converter and setup requirements before relying on a library.

## Further reading
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Daisy Seed datasheet v1.2.0 (codec and output pages) — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [PCM3060 datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm3060.pdf)
- [Getting started: audio — Electro-Smith](https://docs.daisy.audio/tutorials/_a3_Getting-Started-Audio/)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi DAC+ (PCM5122) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/dac_plus.adoc)
- [I²S — Wikipedia](https://en.wikipedia.org/wiki/I%C2%B2S)
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
