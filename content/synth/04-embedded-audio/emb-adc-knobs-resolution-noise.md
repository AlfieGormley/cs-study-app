---
id: emb-adc-knobs-resolution-noise
sourceLesson: emb-adc-knobs
title: "ADC codes and usable resolution"
level: intermediate
minutes: 4
summary: "An ideal converter has a power-of-two number of codes and a defined voltage per code."
---

A knob on a synth is a potentiometer wired as a voltage divider. Turning it changes a voltage between 0 V and 3.3 V. An **ADC** (analogue-to-digital converter) measures that voltage and hands the firmware a number. Everything between "the user turned the knob" and "the filter cutoff moved" happens in this lesson, and almost all of it is about dealing with imperfection: noise, jitter and the mismatch between how knobs turn and how ears hear.

## How an ADC works

An ADC repeatedly samples a voltage and **quantises** it to an integer code. Three numbers describe it:

- **Resolution.** How many bits each reading has. More bits means more distinct codes. A 12-bit ADC gives 4,096 codes (0 to 4,095).
- **Reference voltage.** The voltage that corresponds to full scale. On both the Daisy Seed and Teensy 4.1 the analogue input range is 0–3.3 V.
- **Sample rate.** How often it converts. Audio ADCs use the supported audio sample rates, such as 44.1 or 48 kHz; 48 kHz is not a universal minimum. For knobs, a few hundred to a thousand readings per second is plenty, because hands move slowly.

Each extra bit doubles the number of codes, because every existing pattern can now end in a 0 or a 1:

```formula
codes = 2^N
codes = 2^12 = 4096
where
codes: the number of distinct output values the ADC can produce (they run from 0 to codes − 1)
N: the ADC's resolution, in bits; here 12
2^N: 2 raised to the power N, that is, N copies of 2 multiplied together
In words: every extra bit doubles the number of codes, so 10 bits give 1,024, 12 bits give 4,096 and 16 bits give 65,536.
```

The input range is divided evenly between those codes. The ideal spacing between neighbouring code levels is called one **LSB** (least significant bit), because it is what a change in the lowest bit of the code is worth:

```formula
LSB = V_ref / 2^N
LSB = 3.3 V / 2^12
LSB = 3.3 V / 4096 ≈ 0.000806 V ≈ 0.81 mV
where
LSB: the voltage step between two neighbouring codes, in volts (V)
V_ref: the reference voltage, the input voltage that corresponds to full scale, in volts (V); here 3.3 V
N: the resolution, in bits; here 12
2^N: 2 raised to the power N, the number of codes
V: volt, the unit of voltage
mV: millivolt, one thousandth of a volt
≈: approximately equal to (the result is rounded)
In words: split the 3.3 V range into 4,096 equal steps and each step is about 0.8 mV; every extra bit halves the step.
```

The same sum for three common resolutions:

```python
# Ideal full-scale span in volts.
vref = 3.3
for bits in (10, 12, 16):
    # Divide span by the number of codes.
    lsb = vref / 2**bits
    print(f"{bits}-bit: {2**bits} codes, "
          f"LSB {lsb*1e3:.4f} mV")
```

```output
10-bit: 1024 codes, LSB 3.2227 mV
12-bit: 4096 codes, LSB 0.8057 mV
16-bit: 65536 codes, LSB 0.0504 mV
```

At 16 bits, one code is about 50 µV. Supply noise, wiring pick-up, converter noise and reference quality can limit the usable bits; measure the actual circuit rather than assuming the nominal code width equals accuracy. Resolution is not the same as accuracy. PJRC says this plainly for Teensy 4.1: the default resolution is 10 bits, the hardware allows 12, "but in practice only up to 10 bits are normally usable due to noise". Electro-Smith describes the Daisy Seed's ADC as "up to 16-bits", returning a float from 0.0 to 1.0 via `GetFloat()`.

For a knob, 7 bits (128 steps, like a MIDI CC) is coarse; 10 usable bits (1,024 steps) is usually smooth enough, especially once you smooth and map the value.

## Key takeaways
- An ideal converter has a power-of-two number of codes and a defined voltage per code.
- Nominal resolution does not establish accuracy or noise-free resolution.

## Further reading
- [Getting started: ADCs — Electro-Smith](https://docs.daisy.audio/tutorials/_a4_Getting-Started-ADCs/)
- [Teensy 4.1 analog pins — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Coding schemes used with data converters (SBAA042) — Texas Instruments](https://www.ti.com/lit/an/sbaa042/sbaa042.pdf)
- [Analog-to-digital converter — Wikipedia](https://en.wikipedia.org/wiki/Analog-to-digital_converter)
- [Introduction to Digital Filters (one-pole filters) — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/filters/)
