---
id: midi-audio-levels-load-bridging
title: Check the output and input impedances
level: intermediate
minutes: 3
sourceLesson: midi-audio-levels
summary: Model the resistive divider, then check the real output driver’s load and current ratings rather than extrapolating beyond them.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Impedance bridging

Audio line connections are not impedance-*matched* (that is for power transfer and radio). They use **impedance bridging**: a **low output impedance** drives a **high input impedance**. A line driver is normally specified for a minimum load impedance; the receiver should present a much higher impedance than the source. These are design and product specifications, not fixed universal values.

Why does this work? In a simple resistive (Thévenin) model, the output impedance and the input impedance form a **voltage divider**: the source's voltage is shared between its own output impedance and the input impedance in proportion to their sizes, and only the input's share reaches the next stage.

```formula essential
V_in = (V_src Z_in) / (Z_out + Z_in)
where
V_in: the voltage that actually arrives at the input, in volts (V)
V_src: the voltage the source generates internally, before its own output impedance, in volts
Z_in: the input impedance of the receiving device, in ohms (Ω)
Z_out: the output impedance of the source, in ohms
V: volt
Ω: ohm, the unit of resistance and impedance
In words: the larger the input impedance compared with the output impedance, the closer the received voltage is to the full source voltage; when the load is much smaller than the output impedance, most of the voltage is lost inside the source.
```

The Digitakt's main outputs have a 440 Ω output impedance (Elektron's figure, unbalanced). Here is what the divider predicts for a 1 V source with that output impedance as the load changes:

| Load | Voltage arriving | Level change |
|---|---|---|
| 10 kΩ line input | about 0.96 V | about −0.4 dB |
| 1 kΩ | about 0.69 V | about −3.2 dB |
| 32 Ω headphones | about 0.07 V | about −23 dB |
| 8 Ω speaker | about 0.02 V | about −35 dB |

Into a 10 kΩ line input almost nothing is lost: that is bridging working as intended. Into a 32 Ω headphone or an 8 Ω speaker, nearly all the voltage is dropped inside the source, and the output stage is asked for far more current than it was designed for. That is the reason line, headphone and speaker connections are not interchangeable.

The calculations are a linear resistive model, not proof that a real driver remains linear into headphones or a speaker. Outside its rated load it can limit current, distort, overheat or become unstable. Design the synth output for the actual receiving input and follow the buffer or codec driver's documented minimum load.

## Key takeaways
- Audio line connections bridge rather than match: a low output impedance drives a much higher input impedance.
- Output and input impedances form a voltage divider, so a high-impedance input receives nearly all the voltage while a low-impedance load steals most of it.
- The divider is a simple model; check the real driver's minimum load and current ratings instead of extrapolating beyond them.

## Further reading
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Nominal level — Wikipedia](https://en.wikipedia.org/wiki/Nominal_level)
- [Impedance bridging — Wikipedia](https://en.wikipedia.org/wiki/Impedance_bridging)
- [Balanced audio — Wikipedia](https://en.wikipedia.org/wiki/Balanced_audio)
- [Capacitive coupling (coupling capacitors and their high-pass effect) — Wikipedia](https://en.wikipedia.org/wiki/Capacitive_coupling)
- [Phantom power — Wikipedia](https://en.wikipedia.org/wiki/Phantom_power)
- [Single-supply biasing (op amps biased at half supply, coupling capacitors) — LibreTexts, from J. Fiore's op amp textbook](https://eng.libretexts.org/Workbench/Introduction_to_Circuit_Analysis/05%3A_Advanced_Topic-_Operational_Amplifiers/5.10%3A_Basic_Op_Amp_Circuits/5.10.03%3A_Single_Supply_Biasing)
- [Single-Supply Op Amp Design Techniques (SLOA030) — Texas Instruments](https://www.ti.com/lit/an/sloa030a/sloa030a.pdf)
- [PCM5102A data sheet (ground-centred 2.1 V RMS output) — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
- [Digitakt II user manual, technical information — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
