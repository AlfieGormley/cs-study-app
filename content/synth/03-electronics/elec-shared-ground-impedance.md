---
id: elec-shared-ground-impedance
sourceLesson: elec-noise-grounding
title: "Shared return impedance and analogue grounding"
level: advanced
minutes: 3
summary: "Separate noisy return currents from sensitive references."
---

Separate noisy return currents from sensitive references.

## Shared impedance and star grounding
Ground loops are one mechanism. The other, inside your own circuit, is **shared-impedance coupling**. Every ground wire or track has resistance (and inductance). If a noisy current, such as an LED being multiplexed, a processor, or a display, returns through the same piece of ground wire as an audio signal's reference, the voltage that current makes across the shared wire appears in the audio:

```formula
V_noise = I_noisy R_shared
V_noise = 0.1 A × 0.05 Ω = 0.005 V = 5 mV
where
V_noise: the voltage added to the audio's ground reference, in volts (V)
I_noisy: the noisy return current sharing the wire, here 100 mA = 0.1 amperes (A) of LED current
R_shared: the resistance of the shared stretch of ground wire, here 0.05 ohms (Ω)
V: volts
A: amperes
Ω: ohms
mV: millivolts; 1 mV = 0.001 V
In words: 100 mA of LED current through a twentieth of an ohm of shared wire shifts the audio's ground by 5 mV, in step with the LEDs. This is a 5 mV reference shift. If an unwanted variation is 5 mV RMS, its level is roughly 36 dB below a 0.316 V RMS signal; audibility depends on gain, spectrum and listening conditions. The LED-current magnitude alone does not specify its noise RMS level.
```

The figures are illustrative; the fix is to stop the noisy current sharing the wire at all.

```diagram
 BAD: daisy-chained ground
 audio ──┬── LEDs ──┬── MCU ──┬── supply −
         └ shared wire carries all returns

 GOOD: star ground
          audio   LEDs    MCU
            │       │      │
            └───────┼──────┘
                    ● star point
                    │
                supply −
```

**Star grounding** (single-point grounding) at an introductory level means:

- Each sub-circuit has its own return wire to one common point.
- High-current and noisy returns don't share wire with sensitive audio returns.
- The star point is usually at the power entry or where the audio reference is defined.

You won't build perfect stars on a breadboard. Apply the principle with intent: give the audio output's ground its own wire back to the board's ground pin, and keep LED and motor returns off it.

## Analogue and digital ground
Boards with audio codecs often talk about **AGND** (analogue ground) and **DGND** (digital ground). At a conceptual level:

- Digital circuits produce large, fast, spiky return currents.
- Analogue audio needs a quiet, stable reference.
- Layout keeps noisy digital return currents away from sensitive analogue references. Often this uses careful placement over a **continuous ground plane**; a split plane or one-point join is not a universal requirement.

Two cautions:

- **Use the specified grounding topology.** AGND and DGND must have the connection required by the manufacturer, often both directly to one low-impedance plane. Splitting that plane or forcing a distant single-point join can worsen high-frequency current return paths.
- **Follow the manufacturer.** If your audio board exposes separate analogue and digital ground pins, connect pots, audio jacks and analogue parts as its documentation directs. Codec datasheets specify their own grounding and layout. This is advanced material; for the first build, follow the board's guidance and keep noisy and quiet wiring physically apart.

## Key takeaways

- Separate noisy return currents from sensitive references.
- Follow the board’s grounding topology; a split plane is not universal.

## Further reading

- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
