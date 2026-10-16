---
id: aud-enclosures-port-tuning
title: Estimate a port’s tuning frequency
level: intermediate
minutes: 4
summary: Box air acts as a spring and the port air as a moving mass.
sourceLesson: aud-enclosures
---

## Port tuning: Helmholtz intuition

A port behaves like the neck of a bottle. The air plug in the port is a mass bouncing on the springy air in the box. That is a **Helmholtz resonator**, and its resonance (the box tuning) is:

```formula
Fb = (c / (2π)) √(A / (Vb Leff))
where
Fb: the box tuning frequency, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
π: pi, about 3.14159
√: square root
A: the port's cross-sectional area, in square metres (m^2); for a round port, π × r^2 where r is its radius
Vb: the internal box volume, in cubic metres (m^3); 1 L = 0.001 m^3
Leff: the port's effective length, in metres (m): its physical length plus an end correction (see below)
Hz: hertz, cycles per second
In words: a bigger box or a longer port lowers the tuning; a wider port raises it.
```

The air just beyond each open end of the port moves with the plug too, so the port acts longer than it is. That extra is the **end correction**:

```formula
Leff = Lp + kr
where
Leff: the effective acoustic length of the port, in metres (m)
Lp: the physical length of the port tube, in metres (m)
k: the total end-correction factor for both ends (no unit): about 0.61 for an end that stops in free air, about 0.85 for an end flush with a flat panel; one of each gives about 1.46
r: the port's radius, in metres (m)
In words: add roughly one and a half port radii to the tube length when one end is flush with the baffle and the other is free inside the box.
```

Because the area is under the square root and divided by the length, a wider port must also be longer to keep the same Fb. Worked example: a 30 L box with a 5 cm diameter port, 15 cm long, with a total radius-based end-correction factor of 1.46:

```formula
A = π(0.025 m)^2 ≈ 0.00196 m^2
Leff = 0.15 m + 1.46 × 0.025 m
Leff ≈ 0.1865 m
Vb Leff = 0.03 m^3 × 0.1865 m
Vb Leff ≈ 0.005595 m^4
Fb = ((343 m/s) / (2π))
     × √(0.00196 m^2 / 0.005595 m^4)
Fb ≈ (54.6 m/s) × (0.592 / m)
Fb ≈ 32.3 Hz
where
A: the port's cross-sectional area, in square metres (m^2); the radius is half of 5 cm, 0.025 m
π: pi, about 3.14159
Leff: the effective port length, in metres (m)
Vb: the box volume, in cubic metres (m^3); 30 L = 0.03 m^3
Fb: the box tuning frequency, in hertz (Hz)
√: square root
m: metre, the unit of length
s: second, the unit of time
Hz: hertz, cycles per second; m/s divided by √(m^2) gives 1/s, which is Hz
≈: approximately equal to
In words: this 30 L box with a 5 cm × 15 cm port tunes to about 32 Hz; without end corrections it would be about 36 Hz.
```

The same sum as code:

```python
import math

c = 343
def fb(vb_litres, d, length, k=0.0):
    a = math.pi * (d / 2) ** 2
    # Include air moving just beyond the
    # ends.
    leff = length + k * (d / 2)
    return (c / (2 * math.pi)) * math.sqrt(
        a / (vb_litres / 1000 * leff))

# 30 L box, 5 cm port, 15 cm long
print(round(fb(30, 0.05, 0.15), 1))
# with end corrections ~1.46 x radius
print(round(fb(30, 0.05, 0.15, 1.46), 1))
```

```
36.1
32.3
```

End correction moves the tuning by several hertz here. Real designs are modelled in software and checked by measurement (the impedance curve of a ported box has two peaks with a dip at Fb, which is an easy way to find the true tuning).

## Key takeaways
- Box air acts as a spring and the port air as a moving mass.
- Tuning depends on port area, box volume and effective length.
- End corrections are geometry-dependent; model and measure the actual cabinet.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
