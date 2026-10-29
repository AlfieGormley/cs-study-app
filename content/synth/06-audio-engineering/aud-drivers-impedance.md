---
id: aud-drivers-impedance
title: Read a driver’s impedance curve
level: intermediate
minutes: 4
summary: An impedance label does not mean constant impedance at every frequency.
sourceLesson: aud-drivers
---

## Impedance: nominal vs reality

An "8 Ω" speaker isn't 8 Ω. Its impedance depends on frequency:

- At DC it's just the voice-coil resistance, **Re** (often around 5–7 Ω for an "8 Ω" driver).
- Near **Fs** it rises to a sharp peak, because the back-EMF of the resonating cone opposes the current.
- Above resonance it falls to a minimum, then rises again at high frequencies because the voice coil is an **inductor**.

A simple electrical model adds up three parts: the coil's resistance, the coil’s inductive impedance (which grows with frequency), and a "motional" part caused by the cone's movement, which peaks at resonance. Impedance is really a complex number, because it also shifts the timing (phase) of the current; the *size* of the total is what an impedance plot shows.

Purdue's sample woofer (6.6 Ω coil resistance, 0.48 mH inductance, 65 Hz free-air resonance, electrical Q of 0.436 and mechanical Q of 2.25) shows how much the size varies in that simple model:

| Frequency | Approximate impedance |
|---|---|
| 20 Hz | 8.9 Ω |
| 65 Hz (Fs) | 40.7 Ω |
| 200 Hz | 8.9 Ω |
| 600 Hz | 6.7 Ω |
| 2 kHz | 8.6 Ω |
| 10 kHz | 30.8 Ω |

From 6.7 Ω to over 40 Ω across the band. Real voice-coil inductance is lossy, so the high-frequency rise is usually gentler than this simple model shows.

The resonance peak's height depends on how the resonance is damped. A lightly damped suspension (high mechanical Q) gives a tall, sharp peak and a lossy suspension (low mechanical Q) a lower, broader one. A stronger motor, which has a lower electrical Q, makes the peak taller still, because the moving coil generates more back-EMF. This is also how Fs and the two Qs are measured: from the shape of the impedance curve.

```formula reference
Z_max = R_e (1 + Q_ms / Q_es)
where
Z_max: the impedance at the resonance peak, in ohms (Ω), neglecting voice-coil inductance
R_e: the voice coil's DC resistance (Re on datasheets), in ohms (Ω)
Q_ms: the mechanical Q (Qms): how sharp the resonance is from suspension losses alone; a pure number, roughly 0.5–10 and often about 3
Q_es: the electrical Q (Qes): how strongly the motor's electrical damping controls the resonance; a pure number, typically about 0.2–1
Ω: ohm, the unit of impedance and resistance
In words: The resonance peak is the coil resistance multiplied up by one plus the ratio of the mechanical Q to the electrical Q, so a sharper mechanical resonance gives a taller peak; the Purdue sample reaches about 41 ohms.
```

**Nominal impedance** is a single rounded label for the region above resonance. The loudspeaker standard IEC 60268-5 says the minimum impedance in the rated frequency range should not fall below **80% of the rated (nominal) impedance**: an "8 Ω" speaker should not dip below 6.4 Ω in its working range. Not every manufacturer follows that rule, and real multi-way speakers with crossovers can dip well below their label, which is why amplifier makers care about the *minimum*, not the nominal (the power-amplifier lessons).

## Key takeaways
- An impedance label does not mean constant impedance at every frequency.
- Resonance, coil resistance and inductance shape the curve.
- Amplifier compatibility requires the load’s magnitude and phase, not just its nominal label.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
