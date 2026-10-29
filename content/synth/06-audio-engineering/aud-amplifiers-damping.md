---
id: aud-amplifiers-damping
title: Understand damping factor and cable loss
level: advanced
minutes: 3
summary: Damping factor compares load impedance with amplifier source impedance.
sourceLesson: aud-amplifiers
---

## Damping factor

**Damping factor** is the ratio of the speaker's nominal impedance to the amp's **output impedance**: how many times smaller the amp's own internal impedance is than the speaker's. An amp with 0.01 Ω output impedance driving 8 Ω has a damping factor of 800.

A low output impedance lets the amp's back-EMF path control the driver's motion near resonance (the loudspeaker-driver lessons: the driver is also a generator, and the amplifier's low impedance acts as a brake on it). Above a modest value (tens) the audible benefit is small, because the **speaker cable** and the driver's own voice-coil resistance dominate.

The cable's resistance adds to the amp's output impedance, and current flows through both conductors, out and back. Ten metres of 1.5 mm² copper cable is 20 m of conductor, about 0.22 Ω: over twenty times a good amplifier's 0.01 Ω. So what the speaker actually sees is set mostly by the cable:

```formula reference
DF_spk = Z_load / (Z_out + R_c)
where
DF_spk: the damping factor seen at the speaker, including the cable (no unit)
Z_load: the speaker's nominal impedance, in ohms (Ω)
Z_out: the amplifier's output impedance, in ohms (Ω); typically a few hundredths of an ohm for a solid-state amp
R_c: the resistance of the speaker cable, both conductors together, in ohms (Ω); it grows with length and falls with conductor cross-section
Ω: ohms, the unit of resistance
In words: The damping factor at the speaker compares the speaker's impedance with everything in series behind it, so a long, thin cable usually sets the real figure rather than the amplifier.
```

With that 10 m cable, the amplifier's damping factor of 800 becomes about 34 at the speaker. Doubling the amplifier's damping factor would barely change that; halving the cable's resistance (shorter, or twice the copper cross-section) would roughly double it. Use thicker cable for long runs, and treat very high DF claims as marketing.

## Key takeaways
- Damping factor compares load impedance with amplifier source impedance.
- Both cable conductors contribute resistance.
- Long thin cable can dominate the amplifier’s own output resistance.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
