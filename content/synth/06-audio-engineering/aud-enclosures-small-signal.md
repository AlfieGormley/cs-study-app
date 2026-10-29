---
id: aud-enclosures-small-signal
title: Read the driver’s small-signal parameters
level: intermediate
minutes: 4
summary: Moving mass and suspension compliance determine free-air resonance.
sourceLesson: aud-enclosures
---

## Thiele–Small parameters

A driver datasheet lists **Thiele–Small (T/S) parameters**, measured at low levels where the driver behaves linearly. The three you use most:

- **Fs**: the free-air resonance (moving mass on the suspension spring).
- **Qts**: the total Q at Fs: how damped the resonance is. Purdue's notes put most drivers between about 0.2 and 0.5.
- **Vas**: the volume of air with the same springiness (compliance) as the driver's suspension.

### Fs: a mass on a spring

The cone, voice coil and the air they carry are a mass; the surround and spider are a spring. Like any mass on a spring, they have one natural frequency. A heavier cone or a softer suspension gives a lower resonance: four times the mass halves Fs. For example, a 20 g moving mass on a suspension that moves 1 mm per newton resonates at about 36 Hz.

```formula reference
Fs = 1 / (2π √(Mms Cms))
where
Fs: the driver's free-air resonance frequency, in hertz (Hz)
Mms: the total moving mass (cone, coil and the air load moving with them), in kilograms (kg)
Cms: the mechanical compliance of the suspension: how far it moves per newton of force, in metres per newton (m/N); higher compliance means a softer suspension
π: pi, about 3.14159
√: square root
kg: kilogram, the unit of mass
m: metre, the unit of length
N: newton, the unit of force
Hz: hertz, cycles per second
In words: Like any mass on a spring, the resonance falls as the moving mass or the suspension's softness rises; four times the mass halves the resonance frequency.
```

### Qts: how damped the resonance is

Two things damp the resonance. The suspension loses some energy as heat (the mechanical Q, **Qms**). The voice coil moving in the magnet generates a voltage that the amplifier's low output impedance loads through a low-resistance circuit, which brakes the cone (the electrical Q, **Qes**). They combine like resistors in parallel, so the total is always lower than either part and the smaller one dominates:

```formula reference
Qts = (Qms Qes) / (Qms + Qes)
where
Qts: the total Q of the driver at Fs (no unit); lower means more damped
Qms: the mechanical Q, set by losses in the suspension (no unit); typically several, e.g. 4
Qes: the electrical Q, set by braking from the motor and amplifier (no unit); typically 0.2 to 1, e.g. 0.4
In words: Mechanical and electrical damping combine like resistors in parallel, so the total Q is below both and is dominated by the smaller one, usually the electrical Q.
```

With a mechanical Q of 4 and an electrical Q of 0.4, the total Q is about 0.36, close to the electrical Q. That is typical: the motor does most of the damping. Q has no unit because it is a ratio (stored energy to energy lost per cycle, roughly).

### Vas: the suspension expressed as air

Vas turns the suspension's springiness into "the volume of air that would be just as springy" under the same cone. It grows with the suspension's compliance and with the **square of the cone area**: doubling the cone area quadruples Vas. A roughly 8-inch woofer (about 0.022 m² of cone) with a 1 mm/N suspension has a Vas of about 68 litres.

So for a fixed cone area, larger Vas means a softer suspension. Because Vas grows with cone area squared, it is not a stiffness comparison across arbitrary driver sizes: a big woofer can have a large Vas with a stiff suspension.

Vas matters because it is compared with the box volume: a box much smaller than Vas has an air spring much stiffer than the suspension, so the box, not the driver, sets the system's resonance (next lesson). Factory tolerances are wide (Purdue's notes give about ±15 % on Fs and ±20–30 % on Vas), so measuring your own driver is worthwhile.

## Key takeaways
- Moving mass and suspension compliance determine free-air resonance.
- Mechanical and electrical damping combine into total Q.
- Equivalent compliance volume depends on both cone area and suspension compliance.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
