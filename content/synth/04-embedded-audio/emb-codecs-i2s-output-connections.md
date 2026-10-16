---
id: emb-codecs-i2s-output-connections
sourceLesson: emb-codecs-i2s
title: "Match the analogue output to a load"
level: intermediate
minutes: 4
summary: "Check output type, full-scale level and destination limits together."
---

## The output stage and line level

The codec's DAC output is not always ready to drive a cable. A board's output stage may include a coupling capacitor (to block DC), an op-amp buffer, filtering, and sometimes a headphone amplifier. You do not need to design one to start, but you must know what your board's output is designed for.

Signal levels are often quoted as RMS voltage, the DC magnitude that would deliver the same power averaged over time into the same resistance. The sine full-scale rating is an RMS test level, not the instantaneous peak of arbitrary material. Standard references:

| Level | RMS voltage |
|---|---|
| Consumer line, −10 dBV | 0.316 V |
| Professional line, +4 dBu | 1.228 V |

Those voltages come from the decibel definition: a level in dB is 20 times the base-10 logarithm of a voltage ratio, measured against a fixed reference voltage. Turned around, it gives the voltage for any level:

```formula
V_rms = V_0 10^(L / 20)
V_rms = 1 V × 10^(−10 / 20) ≈ 0.316 V
V_rms = 0.775 V × 10^(4 / 20) ≈ 1.228 V
where
V_rms: the RMS voltage of the signal, in volts (V)
V_0: the reference voltage: 1 V for dBV, 0.775 V (√0.6, more exactly 0.7746 V) for dBu
L: the level in decibels relative to that reference (dBV or dBu); here −10 and +4
10^(L / 20): 10 raised to the power L / 20
V: volt, the unit of voltage
≈: approximately equal to
In words: every 20 dB is a factor of 10 in voltage. Consumer line level is about a third of a volt, professional line level a little over 1.2 V.
```

What the boards document (checked 2026-10-16):

- **Daisy Seed:** line-level outputs, 0 dBFS at 1 V RMS, output impedance 100 Ω; inputs AC coupled, 3.6 V peak-to-peak, which the datasheet calls "approx. 1Vrms" (a sine of 3.6 V p-p is actually about 1.27 V RMS, so treat that figure as rough; see the conversion below).
- **Teensy audio adaptor:** stereo line out and a headphone output, plus line in or mic in.
- **Raspberry Pi DAC+:** line out 0–2 V RMS on phono sockets, plus a headphone amplifier.

For a sine wave, peak-to-peak and RMS voltages are related by a fixed factor, which is how the Daisy figure above was checked:

```formula
V_rms = V_pp / (2 × √2)
V_rms = 3.6 V / (2 × 1.414) ≈ 1.27 V
where
V_rms: the RMS (root-mean-square) voltage of the sine, in volts (V)
V_pp: the peak-to-peak voltage, from the lowest point of the wave to the highest, in volts (V); here 3.6 V
√2: the square root of 2, about 1.414
V: volt, the unit of voltage
≈: approximately equal to
In words: halve the peak-to-peak voltage to get the peak, then divide by about 1.414 to get the RMS value. This holds only for sine waves; other shapes have other ratios.
```

**Line, headphone and speaker outputs are not interchangeable.** A line output expects a high-impedance input (an audio interface's line input). A headphone output can drive tens of ohms. A speaker needs a power amplifier. Plugging a speaker into a line output does not work well and can stress the output stage.

> [!warning] Before connecting to your interface
> Keep to low-voltage, battery or USB-powered setups: no mains wiring. Check the interface manual for its input type and maximum level. Start with the interface gain at minimum and the synth's output low, then raise them. Never connect two outputs together.

## Key takeaways
- Check output type, full-scale level and destination limits together.
- Line, headphone and speaker paths require different drive capabilities.

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
