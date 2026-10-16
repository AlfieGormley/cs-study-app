---
id: emb-adc-knobs-mux-scan
sourceLesson: emb-adc-knobs
title: "Read many knobs with a multiplexer"
level: intermediate
minutes: 2
summary: "Shared select lines let two eight-channel muxes feed two ADC inputs."
---

## Multiplexing many knobs

A synth with 16 knobs may have only 12 ADC pins (the Daisy Seed has 12; the Teensy 4.1 has 18). An **analogue multiplexer** (mux) such as the CD4051 is an 8-to-1 switch: three digital select lines choose which of eight inputs connects to one output. Each select line is one bit, so the number of inputs a mux can choose between doubles with each line:

```formula
channels = 2^s
channels = 2^3 = 8
where
channels: how many inputs the select lines can address
s: the number of digital select lines; here 3 on a CD4051
2^s: 2 raised to the power s, s copies of 2 multiplied together
In words: three select lines give eight combinations (000 to 111), one per input.
```

Two CD4051s read 16 knobs on two ADC pins with three shared select lines.

```
for ch in 0..7:
  set select pins to ch (3 bits)
  wait for the mux output to settle
  value[ch] = read_adc()
```

libDaisy supports this directly: `InitMux` takes an ADC pin, a channel count from 1 to 8 and up to three select pins. Things to watch:

- **Settling time.** After switching, the mux output and ADC input take time to settle to the new knob's voltage. Read too soon and you get a little of the previous knob ("crosstalk"). Allow the documented acquisition/settling time. Discarding an initial reading helps only when the remaining acquisition time is sufficient.
- **Scan rate.** Each knob is read once per full scan, so the ADC behind each mux must convert once per channel per scan. At a 1 kHz scan and eight channels per mux, you need 8,000 conversions a second per ADC, before settling/acquisition overhead; verify the chosen ADC configuration supports it.
- **Supply.** Power the mux from the same supply range as the signals, and keep pot signals within it.

Do the scanning outside the audio callback, or on a timer or DMA, so it never stretches the audio callback deadline.

## Key takeaways
- Shared select lines let two eight-channel muxes feed two ADC inputs.
- Allow documented settling/acquisition time and budget each full scan outside audio work.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
- [CD4051B datasheet — TI](https://www.ti.com/lit/ds/symlink/cd4051b.pdf)
