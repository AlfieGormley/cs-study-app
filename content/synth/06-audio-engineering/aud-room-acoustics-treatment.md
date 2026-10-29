---
id: aud-room-acoustics-treatment
title: Modal transition, absorption and diffusion
level: advanced
minutes: 5
summary: The Schroeder estimate marks a gradual transition rather than a sharp frequency boundary.
sourceLesson: aud-room-acoustics
---

## The modal-to-statistical transition

### The Schroeder frequency

At low frequencies, modes are few and far apart, and the room behaves like a set of resonances. Higher up, modes overlap so densely that the room behaves statistically, as reverberation. The crossover between the two is often estimated by the **Schroeder frequency**. It needs the room's volume and its reverberation time (RT60, the time sound takes to die away by 60 dB, defined in the reverberation lesson). Small rooms and long reverberation times push it up:

```formula reference
f_S ≈ 2000 √(RT60 / V)
where
f_S: the Schroeder frequency, in hertz (Hz): roughly where the room stops acting like separate resonances and starts acting like a smooth reverberant space
≈: approximately equal to; this is a rule-of-thumb estimate, not an exact boundary
2000: a constant that follows from Schroeder's criterion that about three neighbouring modes overlap within each mode's bandwidth (a threshold he chose from measurement experience); it assumes RT60 in seconds and V in cubic metres
√: the square root of the bracket that follows
RT60: the reverberation time, in seconds (s)
V: the room's volume, in cubic metres (m³)
In words: The Schroeder estimate rises with reverberation time and falls with room volume, so a small studio has a wide band of troublesome modal bass, while a large hall's transition sits much lower.
```

For the treated 43.2 m³ studio from the reverberation lesson, with an RT60 of 0.44 s, the estimate is about 200 Hz: below that, the room behaves as separate modes. A large hall can sit far lower, although it can still have audible low-frequency problems.

The transition is gradual, not a sharp line.

Below it, think **room modes** (fix with placement and bass traps). Above it, think **sound reflections** and **reverberation** (fix with absorption and diffusion).

## Absorption vs diffusion

- **Absorbers** convert sound energy to heat. **Porous absorbers** (mineral wool, fibreglass, thick acoustic foam) work by friction as air moves through them. They're most effective where the air particle velocity is high, which is about a **quarter wavelength from a hard wall**. A thin porous panel against a rigid wall generally absorbs low frequencies poorly (the quarter-wavelength rule below shows why). An air gap can improve lower-frequency absorption.
- **Diffusers** scatter sound in many directions without removing much energy. They break up strong specular reflections and flutter echo (rapid repeats between parallel hard walls) while keeping the room feeling live. They need to be large compared with the wavelengths they diffuse, so they work mainly in the mids and highs, and need some distance from the listener.

A good control room usually combines both: absorption where early reflections hit, diffusion or a mix at the back, and bass trapping in the corners.

### The quarter-wavelength rule

For a normally incident plane wave reflected from an ideal rigid wall, the air's particle velocity is zero at the wall and greatest a quarter wavelength away. A porous layer works best where the air moves, so the depth of the material (or of the air gap behind it) roughly sets the lowest frequency it reaches well: the frequency whose quarter wavelength fits between the wall and the material.

| Depth from wall | Frequency whose quarter wavelength fits |
|---|---|
| 5 cm | about 1.7 kHz |
| 10 cm | about 860 Hz |
| 1.4 m | about 60 Hz |

So a 10 cm panel corresponds to roughly 860 Hz, and reaching 60 Hz this way would need about 1.4 m: not practical. This is a rough guide, not a cut-off or a prediction of measured absorption: material flow resistance, thickness, mounting and the angle the sound arrives at all matter, oblique incidence changes the field, and a panel still absorbs something below this frequency.

### Bass traps

Bass wavelengths are metres long, so thin porous panels mounted against a rigid wall generally provide little bass absorption. Thin resonant panel systems are a different mechanism. **Bass traps** are:

- **Thick porous absorbers** (often 10–20 cm or more), commonly placed across **corners**. Straddling a corner leaves a large air gap behind the panel, which extends its effect to lower frequencies.
- **Pressure-based (membrane or Helmholtz) absorbers** tuned to specific low frequencies, which work by resonance and are most effective at pressure maxima such as walls and corners.

For the ideal rigid rectangular model, corners are pressure antinodes for all the mode families. In real rooms, boundaries and coupling differ. Treating them reduces the peaks and decay times of modes across the low end.

## Key takeaways
- The Schroeder estimate marks a gradual transition rather than a sharp frequency boundary.
- Porous absorption depends on thickness, mounting and material properties.
- Quarter-wavelength spacing is an intuition aid, not a hard absorption cutoff.
- Diffusers scatter energy; resonant bass absorbers use a different mechanism from porous panels.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
- [Modal-overlap transition — Treble](https://docs.treble.tech/Transitionfrequency)
- [Acoustic treatment and boundary interference — Genelec](https://www.genelec.com/improving-room-acoustics)
