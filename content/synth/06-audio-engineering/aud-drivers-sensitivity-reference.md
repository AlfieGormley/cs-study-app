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

Why 2.83 V? Into a plain resistance, the power a voltage delivers is the voltage squared divided by the resistance, so 2.83 V into 8 Ω is almost exactly 1 W.

```formula reference
P = V^2 / R
where
P: the electrical power delivered, in watts (W)
V: the RMS voltage across the speaker, in volts (V)
R: the load's (nominal) impedance, treated as a plain resistance, in ohms (Ω)
W: watt, the unit of power
Ω: ohm
In words: Power is voltage squared divided by resistance, so a fixed voltage pushes twice the power into half the resistance: 2.83 volts is 1 watt into 8 ohms but 2 watts into 4 ohms.
```

Using nominal impedance to define the test voltage, the two references agree for 8 Ω. For a **4 Ω** speaker, the same 2.83 V pushes twice the current and **2 W nominal**. Doubling the power adds about 3 dB (the next lesson), so a 4 Ω speaker's voltage-sensitivity figure looks about **3 dB higher** than its 1 W figure. It is not a more efficient speaker; it is simply drawing more power from the amplifier at that voltage.

So before comparing two speakers, convert both figures to the same reference. Actual electrical power also varies with the complex impedance at each frequency, so check the measurement conditions too.

## Key takeaways
- Check whether sensitivity is referred to one watt or 2.83 volts.
- The voltage reference corresponds to about one watt nominal into eight ohms, and two into four ohms.
- In the linear regime, doubling power gives approximately three decibels.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
