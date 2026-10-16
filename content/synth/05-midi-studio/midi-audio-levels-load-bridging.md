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

In this resistive Thevenin model, the output and input impedances form a voltage divider: the source's voltage is shared between its own output impedance and the input impedance in proportion to their sizes, and only the input's share reaches the next stage.

```formula
V_in = (V_src Z_in) / (Z_out + Z_in)
V_in = (1 V × 10000 Ω) / (10440 Ω)
V_in = 1 V × 0.958 ≈ 0.958 V
where
V_in: the voltage that actually arrives at the input, in volts (V)
V_src: the voltage the source generates internally, before its own output impedance, in volts
Z_in: the input impedance of the receiving device, in ohms (Ω); 10 kΩ here
Z_out: the output impedance of the source, in ohms; 440 Ω here (Elektron's figure for the Digitakt)
V: volt
Ω: ohm, the unit of resistance and impedance
≈: approximately equal to (rounded)
In words: the bigger the input impedance compared with the output impedance, the closer the received voltage is to the full source voltage.
```

In decibels a voltage ratio of 0.958 is about −0.4 dB, a negligible loss. The Digitakt's main outputs have a 440 Ω output impedance (Elektron's figure, unbalanced). See what happens to a 1 V signal from a 440 Ω source as the load changes:

```python
def bridged(v_src, z_out, z_in):
    # output and input form a divider
    return v_src * z_in / (z_out + z_in)

import math
# These are ideal resistive load examples.
for z_in in (10_000, 1_000, 32, 8):
    v = bridged(1.0, 440, z_in)
    # The source is 1 V, so v is also
    # the ratio.
    db = 20 * math.log10(v)
    print(f"{z_in:>6} ohm: {v:.3f} V"
          f" ({db:.1f} dB)")
```

```output
 10000 ohm: 0.958 V (-0.4 dB)
  1000 ohm: 0.694 V (-3.2 dB)
    32 ohm: 0.068 V (-23.4 dB)
     8 ohm: 0.018 V (-35.0 dB)
```

Into a 10 kΩ line input, almost nothing is lost. Into a 32 Ω headphone or 8 Ω speaker, nearly all the voltage is dropped inside the source, and the output stage is asked for far more current than it was designed for. That is the numerical reason line, headphone and speaker connections are not interchangeable.

The calculations are a linear resistive model, not proof that a real driver remains linear into headphones or a speaker. Outside its rated load it can limit current, distort, overheat or become unstable. Design the synth output for the actual receiving input and follow the buffer or codec driver's documented minimum load.

## Key takeaways
- Model the resistive divider, then check the real output driver’s load and current ratings rather than extrapolating beyond them.

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
