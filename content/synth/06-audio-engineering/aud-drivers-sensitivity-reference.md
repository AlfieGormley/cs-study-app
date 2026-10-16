---
id: aud-drivers-sensitivity-reference
title: Compare speaker sensitivity references
level: intermediate
minutes: 3
summary: Check whether sensitivity is referred to one watt or 2.83 volts.
sourceLesson: aud-drivers
---

## Sensitivity and the maths of power vs SPL

**Loudspeaker sensitivity** is the SPL on-axis at 1 m for a reference input. Two conventions:

- **dB SPL @ 1 W / 1 m.** One watt into the *nominal* impedance.
- **dB SPL @ 2.83 V / 1 m.** 2.83 V is 1 W into 8 Ω.

Why 2.83 V? The power a voltage delivers into a resistance is:

```formula
P = V^2 / R
P = (2.83 V)^2 / 8 Ω ≈ 1.0 W
P = (2.83 V)^2 / 4 Ω ≈ 2.0 W
where
P: the electrical power delivered, in watts (W)
V: the RMS voltage across the speaker, in volts (V)
R: the load's (nominal) impedance, treated as a plain resistance, in ohms (Ω)
W: watt, the unit of power
Ω: ohm
≈: approximately equal to (rounded)
In words: power is voltage squared divided by resistance, so the same 2.83 V pushes twice the power into 4 Ω as into 8 Ω.
```

Using nominal impedance to define the test voltage, the two references agree for 8 Ω. For **4 Ω**, 2.83 V corresponds to **2 W nominal**, and doubling the power adds about 3 dB (the following power-and-distance unit derives the relationship), making its voltage-sensitivity figure about **3 dB higher**. Actual electrical power varies with complex impedance and frequency; compare the measurement conditions.

## Key takeaways
- Check whether sensitivity is referred to one watt or 2.83 volts.
- The voltage reference corresponds to about one watt nominal into eight ohms, and two into four ohms.
- In the linear regime, doubling power gives approximately three decibels.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
