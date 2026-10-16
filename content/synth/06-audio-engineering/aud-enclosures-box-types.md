---
id: aud-enclosures-box-types
title: Choose an enclosure’s operating principle
level: intermediate
minutes: 4
summary: Ideal sealed and ported boxes have different low-frequency asymptotes.
sourceLesson: aud-enclosures
---

## Four ways to box a driver

### Sealed (closed box, acoustic suspension)

The rear wave is trapped. The air inside acts as an extra **spring** on the cone, which raises the system resonance above the driver's free-air Fs.

- Below the system resonance, Fc, the response falls at **12 dB per octave** (a second-order high-pass).
- Transient behaviour depends on system Q. Sealed boxes are relatively simple to model, and the trapped air adds restoring force at very low frequencies.
- Less efficient in the bass than a ported box of the same size.

### Ported (bass reflex, vented)

A **port tube** (tube) connects the box air to the outside. The air in the port is a mass, the air in the box is a spring: a **Helmholtz resonator**, tuned to a frequency Fb. Around Fb, the port radiates strongly and in phase with the cone's front, adding bass output while the cone barely moves.

- More bass extension or output from the same box volume than sealed.
- Below Fb the response falls at **24 dB per octave** (fourth-order), steeper than sealed.
- **Below Fb the box provides progressively less air-spring loading on the cone**: the suspension and motor still act, but the port increasingly relieves box pressure, so excursion can become excessive. Many ported systems use a subsonic high-pass filter to protect the driver.
- Ports can make noise ("chuffing") if the air speed is too high, usually because the port is too narrow for the output.

### Open baffle

No box at all: the driver sits on a flat panel, open at the back. It stays a **dipole**, radiating front and back with opposite polarity and a null at the sides.

- No box resonances; many listeners like the spacious presentation.
- Front-to-back cancellation adds about **6 dB per octave** of low-frequency roll-off relative to monopole radiation. The driver’s own response also matters: below its mechanical resonance, an unequalised ideal voltage-driven dipole can approach **18 dB per octave** in total. Large baffles, displacement capability and EQ may be needed.
- The rear wave reflects off the wall behind, so placement matters even more.

### Transmission line

The rear wave travels down a long, folded, damped duct before leaving through a vent. The line length is typically chosen as a **quarter wavelength** at the lowest frequency the design targets (often near the driver's resonance), so the line's output reinforces the front at low frequencies while the damping absorbs higher frequencies.

To see how long that is, divide the wavelength by four:

```formula
L_line = c / (4f_t)
L_line = (343 m/s) / (4 × 40 Hz)
L_line ≈ 2.14 m
where
L_line: the length of the transmission line, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
f_t: the target frequency the line is tuned for, in hertz (Hz); here 40 Hz
m: metre, the unit of length
s: second, the unit of time
Hz: hertz, the unit of frequency: one cycle per second
≈: approximately equal to
In words: a line tuned to 40 Hz needs to be about 2.1 m long, which is why lines are folded inside the cabinet.
```

That is a starting estimate: stuffing slows the sound in the line and tapered lines behave differently, so real lines are tuned in modelling software. They're more complex to design and build than sealed or ported boxes.

| Type | Roll-off | Trade-off |
|---|---|---|
| Sealed | 12 dB/oct | Compact, controlled |
| Ported | 24 dB/oct | More output; excursion below Fb |
| Open baffle | Additional ~6 dB/oct dipole loss | Driver roll-off also contributes |
| Transmission line | varies | Complex build |

## Key takeaways
- Ideal sealed and ported boxes have different low-frequency asymptotes.
- A port reduces cone movement near tuning but unloads it progressively below tuning.
- Open baffles and damped transmission lines use rear radiation differently.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
