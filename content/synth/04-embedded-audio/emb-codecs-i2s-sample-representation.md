---
id: emb-codecs-i2s-sample-representation
sourceLesson: emb-codecs-i2s
title: "Convert sample representations"
level: intermediate
minutes: 2
summary: "Signed integer endpoints are asymmetric around zero."
---

## Sample formats

On the wire, codecs use **two's complement integers, MSB first**. The PCM3060 datasheet lists 24-bit I2S, 24-bit left-justified, 24-bit right-justified and 16-bit right-justified, all MSB-first two's complement.

In your code, samples are usually **floats from −1.0 to +1.0**. A library converts at the boundary. libDaisy, for example, converts the codec's 24-bit integers to floats before your callback and back afterwards. The Teensy Audio Library instead works in 16-bit integer blocks throughout.

| Format | Nominal range | Scale magnitude |
|---|---|---|
| 16-bit int | −32,768 … 32,767 | 32,768 |
| 24-bit int | −8,388,608 … 8,388,607 | 8,388,608 |
| float | −1.0 … +1.0 | 1.0 |

The conversion scales the float to the integer range, quantises it and handles the endpoints. A float of 0.5 lands roughly halfway from zero to positive full scale in either format. More bits give finer steps between the same endpoints; they do not make full scale louder.

The top positive code is one less than full scale (8,388,607), because zero takes one of the non-negative codes; an ideal endpoint-saturating converter would map +1.0 to that code rather than overflow. Implementations may deliberately leave more margin. In the libDaisy source fetched on 2026-10-16, the helper clamps its float input to approximately ±0.999985 before multiplying by 8,388,608; a compiled host check of the exact helper returns ±8,388,482 for input ±1.0. It does not reach the extreme 24-bit codes. The audio path also applies output adjustment before conversion; inspect the selected version and configuration. Values beyond full scale **clip** at the conversion, so keep your mix within ±1.0.

## Key takeaways
- Signed integer endpoints are asymmetric around zero.
- Respect the actual library conversion and saturation behavior at the float boundary.

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
- [Exact conversion constants and helper — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/src/daisy_core.h)
