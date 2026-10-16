---
id: aud-enclosures-small-signal
title: Read the driver’s small-signal parameters
level: intermediate
minutes: 5
summary: Moving mass and suspension compliance determine free-air resonance.
sourceLesson: aud-enclosures
---

## Thiele–Small parameters

A driver datasheet lists **Thiele–Small (T/S) parameters**, measured at low levels where the driver behaves linearly. The three you use most:

- **Fs**: the free-air resonance (moving mass on the suspension spring).
- **Qts**: the total Q at Fs: how damped the resonance is. Purdue's notes put most drivers between about 0.2 and 0.5.
- **Vas**: the volume of air with the same springiness (compliance) as the driver's suspension.

### Fs: a mass on a spring

The cone, voice coil and the air they carry are a mass; the surround and spider are a spring. Like any mass on a spring, they have one natural frequency:

```formula
Fs = 1 / (2π √(Mms Cms))
Fs = 1 / (2π √(0.02 kg × 0.001 m/N))
Fs ≈ 35.6 Hz
where
Fs: the driver's free-air resonance frequency, in hertz (Hz)
Mms: the total moving mass (cone, coil and the air load moving with them), in kilograms (kg); here 20 g = 0.02 kg
Cms: the mechanical compliance of the suspension: how far it moves per newton of force, in metres per newton (m/N); here 1 mm/N = 0.001 m/N. Higher compliance means a softer suspension
π: pi, about 3.14159
√: square root
kg: kilogram, the unit of mass
m: metre, the unit of length
N: newton, the unit of force
Hz: hertz, cycles per second
≈: approximately equal to
In words: a heavier cone or a softer suspension gives a lower resonance; four times the mass halves Fs.
```

### Qts: how damped the resonance is

Two things damp the resonance. The suspension loses some energy as heat (the mechanical Q, **Qms**). The voice coil moving in the magnet generates a voltage that the amplifier's low output impedance loads through a low-resistance circuit, which brakes the cone (the electrical Q, **Qes**). They combine like resistors in parallel:

```formula
Qts = (Qms Qes) / (Qms + Qes)
Qts = (4 × 0.4) / (4 + 0.4)
Qts ≈ 0.36
where
Qts: the total Q of the driver at Fs (no unit); lower means more damped
Qms: the mechanical Q, set by losses in the suspension (no unit); typically several, e.g. 4
Qes: the electrical Q, set by braking from the motor and amplifier (no unit); typically 0.2 to 1, e.g. 0.4
In words: the total Q is always lower than either part, and the smaller one (usually Qes) dominates.
```

With mechanical Q four and electrical Q 0.4, total Q is close to the electrical Q. That is typical: the motor does most of the damping. Q has no unit because it is a ratio (stored energy to energy lost per cycle, roughly).

### Vas: the suspension expressed as air

Vas turns the suspension's springiness into "the volume of air that would be just as springy" under the same cone:

```formula
Vas = ρc^2 Sd^2 Cms
Vas = 1.2 kg/m^3 × (343 m/s)^2
      × (0.022 m^2)^2 × 0.001 m/N
Vas ≈ 0.068 m^3 = 68 L
where
Vas: the equivalent compliance volume, in cubic metres (m^3) or litres (L); 1 m^3 = 1000 L
ρ: rho, the density of air, about 1.2 kilograms per cubic metre (kg/m^3) at 20 °C
c: the speed of sound in air, about 343 metres per second (m/s)
Sd: the effective radiating area of the cone, in square metres (m^2); here 0.022 m^2, roughly an 8-inch woofer
Cms: the suspension compliance, in metres per newton (m/N); here 0.001 m/N
m: metre, the unit of length
s: second, the unit of time
kg: kilogram, the unit of mass
N: newton, the unit of force; 1 N = 1 kg·m/s^2, which is why the units cancel down to m^3
L: litre, a volume of 0.001 m^3
≈: approximately equal to
In words: a softer suspension or a bigger cone gives a larger Vas; doubling the cone area quadruples Vas.
```

So for a fixed cone area, larger Vas means a softer suspension. Because Vas grows with cone area squared, it is not a stiffness comparison across arbitrary driver sizes: a big woofer can have a large Vas with a stiff suspension.

## Key takeaways
- Moving mass and suspension compliance determine free-air resonance.
- Mechanical and electrical damping combine into total Q.
- Equivalent compliance volume depends on both cone area and suspension compliance.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
