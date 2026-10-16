---
id: aud-amplifiers-damping
title: Understand damping factor and cable loss
level: advanced
minutes: 3
summary: Damping factor compares load impedance with amplifier source impedance.
sourceLesson: aud-amplifiers
---

## Damping factor

**Damping factor** is the ratio of the speaker's nominal impedance to the amp's **output impedance**:

```formula
DF = Z_load / Z_out
DF = 8 Ω / 0.01 Ω = 800
where
DF: damping factor, a plain ratio (no unit); bigger means the amp holds the driver more firmly
Z_load: the speaker's nominal impedance, in ohms (Ω)
Z_out: the amplifier's output impedance, in ohms (Ω); typically a few hundredths of an ohm for a solid-state amp
Ω: ohms
In words: damping factor says how many times smaller the amp's own internal impedance is than the speaker's.
```

So an amp with 0.01 Ω output impedance into 8 Ω has a damping factor of 800. A low output impedance lets the amp's back-EMF path control the driver's motion near resonance (the loudspeaker-driver units: the driver is also a generator). Above a modest value (tens) the audible benefit is small, because the **speaker cable** and the driver's own voice-coil resistance dominate. The cable's resistance adds to the amp's output impedance:

```formula
R_c = (ρL_w) / A_w
R_c = (1.68 × 10^{-8} Ω·m × 20 m)
      / (1.5 × 10^{-6} m^2)
R_c ≈ 0.224 Ω
DF_spk = Z_load / (Z_out + R_c)
DF_spk = 8 Ω / (0.01 Ω + 0.224 Ω) ≈ 34
where
R_c: the resistance of the speaker cable (both conductors), in ohms (Ω)
ρ: rho, the resistivity of the conductor material, in ohm-metres (Ω·m); assume 1.68 × 10^−8 Ω·m for this illustrative copper-wire calculation; actual resistivity depends on material and temperature
L_w: the total length of conductor the current flows through (out and back), in metres (m): 20 m for a 10 m cable
A_w: the cross-sectional area of each conductor, in square metres (m^2); 1.5 mm² is 1.5 × 10^−6 m^2
DF_spk: the damping factor seen at the speaker, including the cable (no unit)
Z_load: the speaker's nominal impedance, 8 ohms (Ω)
Z_out: the amplifier's output impedance, 0.01 Ω
m: metres
Ω: ohms, the unit of resistance
≈: approximately equal to
In words: a long, thin cable adds far more resistance than a good amp's amplifier power stage, so it sets the real damping factor.
```

Ten metres of 1.5 mm² cable (20 m of conductor) turns DF 800 into about 34. Use thicker cable for long runs, and treat very high DF claims as marketing.

## Key takeaways
- Damping factor compares load impedance with amplifier source impedance.
- Both cable conductors contribute resistance.
- Long thin cable can dominate the amplifier’s own output resistance.

## Further reading
- [Amplifier principles and ratings — Crown](https://www.crownaudio.com/en-US/faq_categories/1)
- [Loudspeaker loads and damping — Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
