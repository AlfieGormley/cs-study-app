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

For a two's-complement integer, the most negative code has the magnitude shown below. A nominal float-to-integer scale uses that magnitude; the actual conversion helper may use a different scale or saturation margin:

```formula
FS = 2^(B − 1)
FS = 2^(24 − 1) = 8388608
s_int ≈ x FS
s_int = 0.5 × 8388608 = 4194304
where
FS: the integer full scale, the size of the most negative code, with no unit
B: the bit depth of the integer format; here 24 (16 for the Teensy library)
2^(B − 1): 2 raised to the power B − 1
s_int: the integer sample code after rounding/truncation and endpoint saturation, with no unit; this simplified relationship describes scaling before those details
x: the float sample from your code, from −1.0 to +1.0
≈: approximately equal to; arbitrary float inputs need quantisation and positive-endpoint saturation
In words: a 24-bit sample runs from −8,388,608 to 8,388,607, so a float of 0.5 becomes about 4.2 million. A float above 1.0 would need a code that does not exist.
```

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
