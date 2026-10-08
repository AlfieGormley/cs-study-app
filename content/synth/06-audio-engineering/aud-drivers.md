---
id: aud-drivers
title: Loudspeaker drivers
level: intermediate
minutes: 17
summary: How a moving-coil driver turns current into sound, the real impedance curve behind the "8 Ω" label, sensitivity at 1 W/1 m and 2.83 V/1 m with the maths linking amplifier power to SPL, frequency response, power handling, driver types from woofer to compression driver and horn, and cone breakup.
---

A loudspeaker **driver** is the motor and diaphragm that actually move air. A loudspeaker *system* is one or more drivers plus an enclosure (lesson 5) and usually a crossover (lesson 6). This lesson is about the driver: how it works, and how to read the numbers on its datasheet.

## The motor structure

Nearly all speakers you will meet are **moving-coil** (electrodynamic) drivers, a design dating from the 1920s.

```diagram
     surround          cone
   ,-----------.  /
  (             )/
   \  +-------+ /      spider
    \ | coil  |/  ===  (suspension)
  [N]=|=gap===|=[N]
  [S]  pole    [S]  <- magnet
       piece
```

The parts:

- **Magnet and pole pieces (the motor).** A permanent magnet (ferrite or neodymium) and steel parts concentrate a strong magnetic field in a narrow ring-shaped **gap**.
- **Voice coil.** A coil of fine wire wound on a light former, sitting in the gap. It's attached to the cone.
- **Cone (diaphragm).** Pushes the air. Paper, polypropylene, aluminium and composites are common. It must be light and stiff.
- **Suspension.** The **surround** at the outer edge and the **spider** behind the cone keep the coil centred in the gap and provide a restoring force that pulls the cone back to rest.
- **Basket (frame)** holds it all together.

## How current becomes sound

A current in a wire in a magnetic field feels a force (the Lorentz force; it's the motor principle). The voice coil is wound so the wire crosses the field at right angles everywhere in the gap, so the force on it is simply:

```formula
F = B × l × i
F = Bl × i
where
F: the force on the voice coil (and so on the cone), in newtons (N)
B: the magnetic flux density in the gap, how strong the magnet's field is there, in tesla (T); around 1 T is typical
l: the length of voice-coil wire sitting in the field, in metres (m); often several metres of fine wire
i: the current through the voice coil, in amperes (A)
Bl: the product B × l, quoted on datasheets as the "force factor" or "BL", in tesla-metres (T·m); typically about 5–20 T·m
N: newton, the unit of force
T: tesla, the unit of magnetic flux density
m: metre
A: ampere, the unit of current
In words: the push on the cone is proportional to the current; a stronger magnet or more wire in the gap gives more push per amp.
```

Datasheets quote the product **Bl** ("BL") because B and l only ever appear together. For example, with 1 A in the coil of a 7 T·m driver:

```formula
F = Bl × i = 7 T·m × 1 A = 7 N
where
F: the force on the voice coil, in newtons (N)
Bl: the force factor, here 7 tesla-metres (T·m)
i: the voice-coil current, here 1 ampere (A)
T: tesla
m: metre
A: ampere
N: newton
In words: 7 T·m of force factor turns each amp into 7 newtons of push.
```

Audio current alternates, so the force alternates and the cone moves back and forth, pushing air (lesson 1).

The cone, coil and the air it carries have **mass**; the suspension acts as a **spring**. Mass on a spring has a resonance. That's the driver's **free-air resonance, Fs**, one of the Thiele–Small parameters in lesson 5. Below Fs the output falls away.

A driver is also a **generator**: a moving coil in a field produces a voltage (back-EMF), exactly as a dynamic mic does. That back-EMF is why the impedance changes so much near resonance.

## Impedance: nominal vs reality

An "8 Ω" speaker isn't 8 Ω. Its impedance depends on frequency:

- At DC it's just the voice-coil resistance, **Re** (often around 5–7 Ω for an "8 Ω" driver).
- Near **Fs** it rises to a sharp peak, because the back-EMF of the resonating cone opposes the current.
- Above resonance it falls to a minimum, then rises again at high frequencies because the voice coil is an **inductor**.

A simple model adds up three parts: the coil's resistance, the coil's inductance (which grows with frequency), and a "motional" part that peaks at resonance. Impedance is a complex number, because it also shifts the timing (phase) of the current; the *size* of the total is what an impedance plot shows.

```formula
Z(f) = R_e + Z_L + Z_m
Z_L = j × 2 × π × f × L_e
Z_m = R_res / (1 + j × x)
x = Q_ms × (f / F_s − F_s / f)
R_res = R_e × Q_ms / Q_es
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

At resonance x = 0, so the motional part is its full R_res. With Purdue's sample woofer (Re = 6.6 Ω, Le = 0.48 mH, Fs = 65 Hz, Qes = 0.436, Qms = 2.25):

```formula
R_res = 6.6 Ω × 2.25 / 0.436 ≈ 34.1 Ω
Z_L = j × 2 × π × 65 × 0.00048 ≈ j × 0.2 Ω
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
Z_min ≥ 0.8 × Z_nom
Z_min ≥ 0.8 × 8 Ω = 6.4 Ω
where
Z_min: the lowest impedance in the rated frequency range, in ohms (Ω)
Z_nom: the rated (nominal) impedance on the label, in ohms (Ω)
≥: is at least (greater than or equal to)
Ω: ohm
In words: a speaker labelled 8 Ω shouldn't dip below 6.4 Ω in its working range.
```

 Not every manufacturer follows that rule, and real multi-way speakers with crossovers can dip well below their label, which is why amplifier makers care about the *minimum*, not the nominal (lesson 7).

## Sensitivity and the maths of power vs SPL

**Sensitivity** is the SPL on-axis at 1 m for a reference input. Two conventions:

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

Using nominal impedance to define the test voltage, the two references agree for 8 Ω. For **4 Ω**, 2.83 V corresponds to **2 W nominal**, and doubling the power adds about 3 dB (see the next formula), making its voltage-sensitivity figure about **3 dB higher**. Actual electrical power varies with complex impedance and frequency; compare the measurement conditions.

To predict how loud a speaker will be, start from its sensitivity, add the decibels gained by using more than 1 W, and subtract the decibels lost by listening further away than 1 m. For a fixed signal spectrum in the linear range, use this approximate on-axis free-field, far-field estimate (neglecting air absorption and power compression):

```formula
SPL = S + 10 × log_10(P / 1 W)
      − 20 × log_10(r / 1 m)
where
SPL: the sound pressure level at the listener, in decibels (dB SPL)
S: the speaker's sensitivity, in dB SPL at 1 W / 1 m; typically 84–90 dB for hi-fi, over 100 dB for PA horns
P: the amplifier power into the speaker's nominal impedance, in watts (W)
r: the listening distance from the speaker, in metres (m); at least about 1 m (the far field)
log_10: the base-10 logarithm
W: watt
m: metre
dB: decibel
In words: every doubling of power adds about 3 dB (10 × log_10 because power is already a power quantity), and every doubling of distance takes away about 6 dB (20 × log_10, the inverse square law for pressure).
```

Each **doubling of power adds only 3 dB**; ten times the power adds 10 dB. For an 87 dB/1 W/1 m speaker at 1 m (so the distance term is zero):

```formula
SPL = 87 + 10 × log_10(100 W / 1 W)
SPL = 87 dB + 20 dB = 107 dB SPL
P = 1 W × 10^{(L_t − S)/10}
P = 1 W × 10^{(105 − 87)/10} ≈ 63 W
where
SPL: the level at 1 m, in dB SPL
P: the amplifier power, in watts (W)
L_t: the target level, here 105 dB SPL
S: the sensitivity, here 87 dB at 1 W / 1 m
log_10: the base-10 logarithm
10^{…}: ten to the power of the bracket; it undoes 10 × log_10, turning decibels back into a power ratio
W: watt
dB: decibel
≈: approximately equal to (rounded)
In words: 100 W gives 20 dB more than 1 W; going the other way, reaching 105 dB SPL needs 18 dB more than 1 W, which is about 63 W.
```

The same in Python:

```python
import math

sens = 87  # dB SPL, 1 W / 1 m
for p in (1, 2, 10, 100):
    spl = sens + 10 * math.log10(p)
    print(f"{p:>3} W: {spl:5.1f} dB @ 1 m")

# power for 105 dB SPL at 1 m:
print(round(10 ** ((105 - sens) / 10), 1))
```

```
  1 W:  87.0 dB @ 1 m
  2 W:  90.0 dB @ 1 m
 10 W:  97.0 dB @ 1 m
100 W: 107.0 dB @ 1 m
63.1
```

Worked example (from Purdue's notes): you want 90 dB SPL at 4 m outdoors from an 86 dB/1 W/1 m speaker. Work backwards: first the distance loss, then the level needed at 1 m, then the power.

```formula
D = 20 × log_10(4 m / 1 m) ≈ 12 dB
L_1 = 90 dB + 12 dB = 102 dB SPL
L_1 − S = 102 dB − 86 dB = 16 dB
P = 1 W × 10^{16/10} ≈ 40 W
where
D: the level lost between 1 m and 4 m, in decibels (dB)
L_1: the level needed at 1 m, in dB SPL
S: the speaker's sensitivity, 86 dB SPL at 1 W / 1 m
P: the amplifier power needed, in watts (W)
log_10: the base-10 logarithm
10^{…}: ten to the power of the bracket, turning decibels back into a power ratio
m: metre
W: watt
dB: decibel
SPL: sound pressure level
≈: approximately equal to (rounded)
In words: 4 m costs about 12 dB, so you need 102 dB at 1 m, 16 dB above the 1 W figure, which is about 40 times the power: **40 W**, before any headroom for peaks.
```

Every 3 dB of sensitivity halves the amplifier power needed for the same level. Sensitivity is closely related to **efficiency**, the fraction of electrical power that comes out as sound:

```formula
η = P_ac / P_el
P_ac = 0.01 × 40 W = 0.4 W
where
η: eta, the efficiency, a fraction (or percentage); around 0.01 (1%) for a typical home loudspeaker
P_ac: the acoustic power radiated as sound, in watts (W)
P_el: the electrical power from the amplifier, in watts (W)
W: watt
In words: efficiency is sound power out divided by electrical power in; at 1%, 40 W of amplifier power makes only about 0.4 W of sound.
```

The rest becomes heat, mostly in the voice coil.

## Frequency response

A frequency response plot shows on-axis SPL (at a fixed input) against frequency. Look for:

- The **usable range**, often given as ±3 dB limits, with the low-frequency limit set mainly by Fs and the enclosure.
- **Smoothness**: narrow peaks often come from cone breakup or cabinet resonance.
- **Off-axis curves**: how the response changes at 30° or 60°. Because of diffraction, a driver radiates widely when its wavelength is large compared with the cone, and **beams** (narrows its dispersion) when the wavelength becomes comparable with the cone.

Where does beaming start? Treat the cone as a flat, rigid disc (a "piston"). Directivity becomes significant when the cone's circumference is about one wavelength, which acousticians write as "ka = 1":

```formula
k × a = 1
k = 2 × π × f / c
f_beam = c / (2 × π × a)
where
k: the wavenumber, 2π divided by the wavelength, in radians per metre (rad/m); higher frequency means bigger k
a: the effective radius of the cone (half its effective diameter), in metres (m)
f: the frequency, in hertz (Hz)
f_beam: the frequency above which the cone starts to focus sound forwards instead of spreading it, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
π: pi, about 3.14159
In words: the bigger the cone, the lower the frequency at which it starts beaming. Double the radius and beaming starts an octave lower.
```

Worked for a woofer with a 13 cm effective diameter and a 25 mm tweeter dome:

```formula
f_beam = 343 / (2 × π × 0.065) ≈ 840 Hz
f_beam = 343 / (2 × π × 0.0125) ≈ 4.4 kHz
where
f_beam: the frequency where beaming becomes significant, in hertz (Hz)
π: pi, about 3.14159
Hz: hertz, cycles per second; kHz is a thousand hertz
kHz: kilohertz
≈: approximately equal to (rounded)
In words: the 6.5 cm-radius woofer beams from about 840 Hz; the 12.5 mm-radius tweeter stays wide up to about 4.4 kHz.
```

(343 is the speed of sound in m/s; 0.065 m and 0.0125 m are the two radii.) The piston model stops being reliable once the cone breaks up (below), so check measured off-axis curves.

That beaming is one reason multi-way speakers hand high frequencies to smaller drivers.

## Power handling

Two separate limits:

- **Thermal.** The voice coil heats up. Too much *average* power for too long burns the coil or its adhesive. Ratings are usually based on long tests with band-limited noise, and the method (and so the number) differs between standards and manufacturers, so read what method a figure refers to.
- **Mechanical (excursion).** At low frequencies the cone must move a long way. **Xmax** describes an excursion limit under a specified geometric or distortion criterion; definitions vary. Motor, suspension and other nonlinearities can limit it. Beyond the useful linear range, distortion increases; far beyond it, the coil can hit the back plate or the suspension can tear. A driver can be over-excursed at low frequencies with modest power, especially below a ported box's tuning frequency (lesson 5).

> [!tip] Power ratings are not targets
> A "100 W" speaker doesn't need 100 W, and isn't safe with any 100 W signal. A clipped signal from a small amplifier can damage a tweeter (lesson 7), while a large, clean amplifier used sensibly is often safer.

## Driver types

| Driver | Typical job | Notes |
|---|---|---|
| Subwoofer | Below ~80–120 Hz | Long excursion, big cone |
| Woofer | Bass (and mids in 2-way) | 13–38 cm common |
| Midrange | ~300 Hz–3 kHz | Covers the vocal region |
| Tweeter | Above ~2–3 kHz | Light dome, 19–28 mm |
| Compression driver + horn | Mid/high in PA | Very high sensitivity |

In a **compression driver**, a diaphragm pressurises a small chamber; sound passes through **phase-plug** channels into a narrow **throat**, and the **horn** flares out to the room. The horn improves the match between the diaphragm and the air, so far more of the electrical power becomes sound. It also controls dispersion, which PA designers use to aim sound at the audience and away from walls. Horn-loaded systems can reach sensitivities around 110 dB SPL at 2.83 V/1 m; a typical hi-fi speaker is in the mid-80s to around 90 dB.

## Cone breakup

At low frequencies a cone moves as a rigid **piston**. As frequency rises, the cone stops moving as one piece: bending waves travel across it, and different parts move with different phase. This is **cone breakup**. It causes:

- Peaks and dips in the response, often a sharp peak near the top of the driver's range.
- Changes in dispersion, and sometimes audible coloration and distortion.

Stiff, light cones (aluminium, ceramic) push breakup higher but often produce a stronger, sharper peak when it happens. Softer, well-damped cones break up earlier but more gently. Either way, the crossover (lesson 6) is chosen so the driver isn't asked to play much in its breakup region.

## Key takeaways
- A moving-coil driver's force is the force factor Bl times the voice-coil current; the suspension and moving mass create a resonance, Fs.
- Impedance varies with frequency: Re at DC, a peak at Fs, a minimum above it, and a rise from coil inductance. IEC 60268-5 expects the in-band minimum to be at least 80% of the nominal rating.
- Sensitivity is SPL at 1 m for 1 W or 2.83 V; for a 4 Ω speaker the 2.83 V figure is 3 dB higher.
- SPL at a distance is sensitivity, plus 3 dB per doubling of power, minus 6 dB per doubling of distance: doubling power gives only +3 dB.
- Power handling has thermal and excursion limits; drivers beam once the cone's circumference is about a wavelength, and break up at higher frequencies.

## Further reading
- [Loudspeaker — Wikipedia](https://en.wikipedia.org/wiki/Loudspeaker)
- [Loudspeaker basics — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Audio/spk.html)
- [Electrodynamic speaker driver — Wikipedia](https://en.wikipedia.org/wiki/Electrodynamic_speaker_driver)
- [Nominal impedance (loudspeakers) — Wikipedia](https://en.wikipedia.org/wiki/Nominal_impedance)
- [Loudspeaker parameters (lecture notes) — D. G. Meyer, Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [What is impedance? (IEC 60268-5 80% rule) — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
- [Compression driver — Wikipedia](https://en.wikipedia.org/wiki/Compression_driver)
