---
id: aud-drivers-impedance
title: Read a driver’s impedance curve
level: intermediate
minutes: 5
summary: An impedance label does not mean constant impedance at every frequency.
sourceLesson: aud-drivers
---

## Impedance: nominal vs reality

An "8 Ω" speaker isn't 8 Ω. Its impedance depends on frequency:

- At DC it's just the voice-coil resistance, **Re** (often around 5–7 Ω for an "8 Ω" driver).
- Near **Fs** it rises to a sharp peak, because the back-EMF of the resonating cone opposes the current.
- Above resonance it falls to a minimum, then rises again at high frequencies because the voice coil is an **inductor**.

A simple model adds up three parts: the coil's resistance, the coil’s inductive impedance (which grows with frequency in this simple model), and a "motional" part that peaks at resonance. Impedance is a complex number, because it also shifts the timing (phase) of the current; the *size* of the total is what an impedance plot shows.

```formula
Z(f) = R_e + Z_L + Z_m
Z_L = 2jπf L_e
Z_m = R_res / (1 + jx)
x = Q_ms (f / F_s − F_s / f)
R_res = (R_e Q_ms) / Q_es
where
Z(f): the driver's total impedance at frequency f, in ohms (Ω); a complex number whose size |Z| is what the impedance curve plots
f: the frequency of the signal, in hertz (Hz)
R_e: the DC resistance of the voice coil (Re on datasheets), in ohms (Ω); often 5–7 Ω for an "8 Ω" driver
Z_L: the impedance of the voice coil's inductance, in ohms (Ω); it rises in proportion to frequency
Z_m: the motional impedance caused by the cone's movement (back-EMF), in ohms (Ω); largest at resonance
L_e: the voice-coil inductance (Le on datasheets), in henries (H); often a fraction of a millihenry
R_res: the peak value of the motional part, reached exactly at F_s, in ohms (Ω)
x: how far the frequency is from resonance, scaled by Q_ms; a pure number, 0 at F_s
F_s: the free-air resonance frequency (Fs), in hertz (Hz)
Q_ms: the mechanical Q (Qms): how sharp the resonance is from suspension losses alone; a pure number, typically 1–10
Q_es: the electrical Q (Qes): how strongly the motor's electrical damping controls the resonance; a pure number, typically 0.2–1
j: the imaginary unit used in electrical engineering (j × j = −1); it marks the part of an impedance that shifts phase
π: pi, about 3.14159
Ω: ohm, the unit of impedance and resistance
Hz: hertz, cycles per second
H: henry, the unit of inductance
In words: the impedance is the coil's resistance, plus an inductive part that grows with frequency, plus a resonant part that peaks at F_s and dies away either side.
```

At resonance the frequency-offset variable is zero, so the motional part reaches its full peak. Purdue’s sample uses 6.6 Ω coil resistance, 0.48 mH inductance, 65 Hz free-air resonance, electrical Q of 0.436 and mechanical Q of 2.25:

```formula
R_res = 6.6 Ω × 2.25 / 0.436 ≈ 34.1 Ω
Z_L = j × 2π × 65 × 0.00048 ≈ j × 0.2 Ω
|Z(F_s)| ≈ 6.6 Ω + 34.1 Ω ≈ 40.7 Ω
where
R_res: the motional peak, in ohms (Ω)
Z_L: the coil inductance's impedance at 65 Hz, tiny here
|Z(F_s)|: the size of the total impedance at the resonance frequency F_s = 65 Hz, in ohms (Ω)
F_s: the free-air resonance frequency, 65 Hz
Z: impedance
j: the imaginary unit; a j × 0.2 Ω part adds almost nothing to the size
π: pi, about 3.14159
Ω: ohm
≈: approximately equal to (rounded)
In words: at 65 Hz the woofer looks like about 41 Ω, more than five times its "8 Ω" label.
```

The model is easier to sweep across frequency in Python (`2j` is Python's way of writing 2 × j):

```python
import math

Re, Le = 6.6, 0.48e-3
Fs, Qes, Qms = 65, 0.436, 2.25
Rres = Re * Qms / Qes  # motional peak

def z(f):
    x = Qms * (f / Fs - Fs / f)
    # Back-EMF adds frequency-dependent
    # load.
    zm = Rres / complex(1, x)
    return Re + 2j*math.pi*f*Le + zm

for f in (20, 65, 200, 600, 2000, 10000):
    mag = abs(z(f))
    print(f"{f:>5} Hz: {mag:5.1f} ohm")
```

```
   20 Hz:   8.9 ohm
   65 Hz:  40.7 ohm
  200 Hz:   8.9 ohm
  600 Hz:   6.7 ohm
 2000 Hz:   8.6 ohm
10000 Hz:  30.8 ohm
```

From 6.7 Ω to over 40 Ω across the band. (Real voice-coil inductance is lossy, so the high-frequency rise is usually gentler than this simple model shows.)

**Nominal impedance** is a single rounded label for the region above resonance. The loudspeaker standard IEC 60268-5 says the minimum impedance in the rated frequency range should not fall below **80% of the rated (nominal) impedance**:

```formula
Z_min ≥ 0.8Z_nom
Z_min ≥ 0.8 × 8 Ω = 6.4 Ω
where
Z_min: the lowest impedance in the rated frequency range, in ohms (Ω)
Z_nom: the rated (nominal) impedance on the label, in ohms (Ω)
≥: is at least (greater than or equal to)
Ω: ohm
In words: a speaker labelled 8 Ω shouldn't dip below 6.4 Ω in its working range.
```

 Not every manufacturer follows that rule, and real multi-way speakers with crossovers can dip well below their label, which is why amplifier makers care about the *minimum*, not the nominal (the power-amplifier units).

## Key takeaways
- An impedance label does not mean constant impedance at every frequency.
- Resonance, coil resistance and inductance shape the curve.
- Amplifier compatibility requires the load’s magnitude and phase, not just its nominal label.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
