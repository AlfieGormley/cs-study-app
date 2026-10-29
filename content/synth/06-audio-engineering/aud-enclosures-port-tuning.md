---
id: aud-enclosures-port-tuning
title: Estimate a port’s tuning frequency
level: intermediate
minutes: 3
summary: Box air acts as a spring and the port air as a moving mass.
sourceLesson: aud-enclosures
---

## Port tuning: Helmholtz intuition

A port behaves like the neck of a bottle. The air plug in the port is a mass bouncing on the springy air in the box. That is a **Helmholtz resonator**, and its resonance is the box tuning, Fb. Three dials set it:

- **A bigger box** is a softer spring: lower tuning.
- **A longer port** is a heavier air plug: lower tuning.
- **A wider port** lets the box air push the plug more easily: higher tuning.

Because the box volume sits under a square root, four times the volume only halves the tuning. And because the port's area and length appear as a ratio, a wider port (used to reduce air speed and chuffing) must also be longer to keep the same tuning.

```formula reference
Fb = (c / (2π)) √(A / (Vb Leff))
where
Fb: the box tuning frequency, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
π: pi, about 3.14159
√: square root
A: the port's cross-sectional area, in square metres (m^2)
Vb: the internal box volume, in cubic metres (m^3); 1 L = 0.001 m^3
Leff: the port's effective length, in metres (m): its physical length plus an end correction
Hz: hertz, cycles per second
In words: The Helmholtz tuning rises with the square root of port area and falls with the square root of box volume and of effective port length, so a bigger box or a longer port lowers it and a wider port raises it.
```

The air just beyond each open end of the port moves with the plug too, so the port acts longer than it is. That extra is the **end correction**: roughly one and a half port radii in total when one end is flush with the baffle and the other is free inside the box. The exact figure depends on the geometry. For example, a 30 L box with a 5 cm diameter, 15 cm long port tunes to about 36 Hz if you ignore end correction, but about 32 Hz with it: several hertz, enough to matter.

Real designs are modelled in software and checked by measurement. The impedance curve of a ported box has two peaks with a dip at Fb, which is an easy way to find the true tuning.

## Key takeaways
- Box air acts as a spring and the port air as a moving mass.
- Tuning depends on port area, box volume and effective length.
- End corrections are geometry-dependent; model and measure the actual cabinet.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
