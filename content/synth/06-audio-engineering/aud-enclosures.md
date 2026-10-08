---
id: aud-enclosures
title: Enclosure design
level: intermediate
minutes: 17
summary: Why a bare driver makes almost no bass, baffle step, sealed, ported, open-baffle and transmission-line designs, Thiele–Small parameters (Fs, Qts, Vas) and the sealed-box equations, Helmholtz port tuning, cabinet resonance and bracing, and what an alignment is.
---

Hold a bare woofer in the air, play a bass line through it, and you get a thin, tinny sound. Mount the same driver in a box and the bass appears. This lesson explains why, and how the box's design shapes the bass response.

It's a deep subject with decades of published theory. The goal here is the concepts and enough of the maths to read a driver datasheet and understand what box-modelling software tells you.

## The acoustic short circuit

When the cone moves forward, it compresses the air in front and rarefies the air behind. The two sides radiate **equal and opposite** pressure waves: the bare driver is a **dipole** (Dan Russell's radiation demo in Further reading shows the field).

At high frequencies the wavelength is short compared with the path from front to back around the cone's edge, so the two waves don't meet in time to cancel much. At low frequencies the wavelength is long, the rear wave easily diffracts round the edge, and it **cancels the front wave**. Air just sloshes from front to back. This is the **acoustic short circuit**, and it's why a bare driver has almost no bass.

```diagram
 bare driver:   front (+)  )  (  rear (-)
                 \_ air sloshes round _/
 on a baffle:   front (+) |  rear (-)
                  longer path, less cancel
```

The cure is to separate front from back:

- A **baffle** (a flat board) lengthens the path, so cancellation starts at a lower frequency.
- An **enclosure** (a box) traps the rear wave completely, or redirects it so it helps.

## Baffle step

Even in a box, the front baffle has a finite size. At high frequencies, where the baffle is large compared with the wavelength, the driver radiates into the **half-space** in front: half a sphere of directions. At low frequencies, where the wavelength is much larger than the baffle, sound wraps round the cabinet and radiates into the **full space**: the whole sphere.

Engineers often call these "2π" and "4π" radiation, after the solid angle each one covers:

```formula
Ω_full = 4 × π sr
Ω_half = 2 × π sr
where
Ω_full: the solid angle of a whole sphere, which a driver fills when it radiates in all directions (full space)
Ω_half: the solid angle of half a sphere, which a driver on a large flat baffle fills (half-space)
π: pi, the ratio of a circle's circumference to its diameter, about 3.14159
sr: steradian, the unit of solid angle: how much of the space around a point a cone of directions covers
In words: half-space is exactly half of all possible directions, so "2π" means "in front of a big wall" and "4π" means "floating in free space".
```

For the same cone motion, radiating into half-space gives twice the sound pressure of full space: the baffle acts like a mirror, adding a coherent "image" source. Doubling pressure is a 6 dB rise, because sound pressure level is 20 times the base-10 logarithm of a pressure ratio:

```formula
ΔL = 20 × log_10(p_half / p_full)
ΔL = 20 × log_10(2)
ΔL ≈ 6.02 dB
where
ΔL: the difference in on-axis level between half-space and full-space radiation, in decibels (dB)
p_half: the on-axis sound pressure when radiating into half-space, in pascals (Pa)
p_full: the on-axis sound pressure for the same cone motion in full space, in pascals (Pa); here p_half = 2 × p_full
log_10: the base-10 logarithm: log_10(x) is the power you raise 10 to in order to get x; log_10(2) ≈ 0.301
≈: approximately equal to
dB: decibel, a logarithmic unit for comparing two levels
In words: twice the pressure is about 6 dB louder, so losing the baffle's mirror effect costs about 6 dB.
```

So as frequency falls and the radiation spreads into full space, a speaker's on-axis response steps down by up to **6 dB** going from high to low frequencies. The transition happens where the wavelength is comparable with the baffle width: a few hundred hertz for a typical bookshelf speaker. This is the ideal figure: the real step is smoother, and nearby walls and floors change it.

Designers compensate with **baffle step compensation**: usually a gentle shelf in the crossover that reduces everything above the step. In a real room, placing the speaker near a wall gives back some of the lost bass, which is why compensation is a judgement call.

## Four ways to box a driver

### Sealed (closed box, acoustic suspension)

The rear wave is trapped. The air inside acts as an extra **spring** on the cone, which raises the system resonance above the driver's free-air Fs.

- Below the system resonance, Fc, the response falls at **12 dB per octave** (a second-order high-pass).
- Transient behaviour depends on system Q. Sealed boxes are relatively simple to model, and the trapped air adds restoring force at very low frequencies.
- Less efficient in the bass than a ported box of the same size.

### Ported (bass reflex, vented)

A **port** (tube) connects the box air to the outside. The air in the port is a mass, the air in the box is a spring: a **Helmholtz resonator**, tuned to a frequency Fb. Around Fb, the port radiates strongly and in phase with the cone's front, adding bass output while the cone barely moves.

- More bass extension or output from the same box volume than sealed.
- Below Fb the response falls at **24 dB per octave** (fourth-order), steeper than sealed.
- **Below Fb the box stops controlling the cone**: the driver behaves almost as if it were in free air, so excursion can rise quickly. Many ported systems use a subsonic high-pass filter to protect the driver.
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
L_line = c / (4 × f_t)
L_line = 343 m/s / (4 × 40 Hz)
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

## Thiele–Small parameters

A driver datasheet lists **Thiele–Small (T/S) parameters**, measured at low levels where the driver behaves linearly. The three you use most:

- **Fs**: the free-air resonance (moving mass on the suspension spring).
- **Qts**: the total Q at Fs: how damped the resonance is. Purdue's notes put most drivers between about 0.2 and 0.5.
- **Vas**: the volume of air with the same springiness (compliance) as the driver's suspension.

### Fs: a mass on a spring

The cone, voice coil and the air they carry are a mass; the surround and spider are a spring. Like any mass on a spring, they have one natural frequency:

```formula
Fs = 1 / (2 × π × √(Mms × Cms))
Fs = 1 / (2 × π × √(0.02 kg × 0.001 m/N))
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

Two things damp the resonance. The suspension loses some energy as heat (the mechanical Q, **Qms**). The voice coil moving in the magnet generates a voltage that the amplifier's low output impedance short-circuits, which brakes the cone (the electrical Q, **Qes**). They combine like resistors in parallel:

```formula
Qts = (Qms × Qes) / (Qms + Qes)
Qts = (4 × 0.4) / (4 + 0.4)
Qts ≈ 0.36
where
Qts: the total Q of the driver at Fs (no unit); lower means more damped
Qms: the mechanical Q, set by losses in the suspension (no unit); typically several, e.g. 4
Qes: the electrical Q, set by braking from the motor and amplifier (no unit); typically 0.2 to 1, e.g. 0.4
In words: the total Q is always lower than either part, and the smaller one (usually Qes) dominates.
```

With Qms = 4 and Qes = 0.4, Qts comes out close to Qes. That is typical: the motor does most of the damping. Q has no unit because it is a ratio (stored energy to energy lost per cycle, roughly).

### Vas: the suspension expressed as air

Vas turns the suspension's springiness into "the volume of air that would be just as springy" under the same cone:

```formula
Vas = ρ × c^2 × Sd^2 × Cms
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

### Efficiency bandwidth product

A rough rule of thumb uses the **efficiency bandwidth product** (EBP):

```formula
EBP = Fs / Qes
EBP = 30 Hz / 0.5
EBP = 60 Hz
where
EBP: the efficiency bandwidth product, in hertz (Hz)
Fs: the free-air resonance, in hertz (Hz); here 30 Hz
Qes: the electrical Q (no unit); here 0.5
Hz: hertz, cycles per second
In words: drivers with an EBP around 50 tend to suit sealed boxes and those around 100 suit ported ones.
```

An EBP of 60 Hz sits near the sealed end. It's a starting point, not a design method: always model the full parameter set.

Manufacturing tolerances are loose: Purdue's notes give typical factory tolerances of about ±15% for Fs and ±20–30% for Vas. Measure your own driver if accuracy matters.

### The sealed-box equations

Put a driver in a sealed box. The air trapped in the box is a second spring pushing on the cone, alongside the suspension. A smaller box is a stiffer spring. The **compliance ratio** says how stiff the box air is compared with the suspension, and both the resonance and its Q rise with the square root of the total stiffness. These are the closed-box results (Small, 1972), used when you choose a box size:

```formula
α = Vas / Vb
Fc = Fs × √(1 + α)
Qtc = Qts × √(1 + α)
where
α: alpha, the compliance ratio (no unit): how many times stiffer the box air is than the driver's suspension
Vas: the driver's equivalent compliance volume, in litres (L)
Vb: the internal volume of the box, in litres (L)
Fc: the resonance frequency of the driver in the box, in hertz (Hz)
Fs: the driver's free-air resonance, in hertz (Hz)
Qtc: the total Q of the driver in the box (no unit); it sets the shape of the bass roll-off
Qts: the driver's total Q in free air (no unit)
√: square root
L: litre, a unit of volume; 1 L = 0.001 m^3
Hz: hertz, cycles per second
In words: a smaller box (bigger α) pushes the resonance up and makes it less damped, both by the same factor √(1 + α).
```

Here is one driver (Fs = 30 Hz, Qts = 0.35, Vas = 60 L) in a 20 L box:

```formula
α = 60 L / 20 L = 3
√(1 + α) = √4 = 2
Fc = 30 Hz × 2 = 60 Hz
Qtc = 0.35 × 2 = 0.70
where
α: alpha, the compliance ratio (no unit)
√: square root
L: litre, a unit of volume
Fc: the in-box resonance, in hertz (Hz)
Qtc: the in-box total Q (no unit)
Hz: hertz, cycles per second
In words: a 20 L box makes this driver resonate at 60 Hz with a Q of 0.70, close to maximally flat.
```

These equations ignore box losses and stuffing, and they assume the box is small compared with the wavelength (true in the bass).

**Qtc** sets the shape of the bass roll-off. The box-and-driver is a second-order high-pass filter, and for that filter the level exactly at Fc depends only on Qtc:

```formula
L_Fc = 20 × log_10(Qtc)
L_Fc = 20 × log_10(0.707)
L_Fc ≈ −3 dB
where
L_Fc: the response at Fc, relative to the flat level well above Fc, in decibels (dB)
Qtc: the in-box total Q (no unit); here 0.707
log_10: the base-10 logarithm: log_10(x) is the power you raise 10 to in order to get x
≈: approximately equal to
dB: decibel, a logarithmic unit for comparing levels
In words: Qtc = 0.5 gives −6 dB at Fc, 0.707 gives −3 dB, and 1.0 gives 0 dB with a hump just above Fc.
```

| Qtc | Behaviour |
|---|---|
| 0.5 | Critically damped, −6 dB at Fc |
| 0.707 | Butterworth: maximally flat, −3 dB at Fc |
| ~1.0–1.1 | Peak before roll-off, "boomier" |

The same sum for three box sizes, as code:

```python
import math

def sealed(fs, qts, vas, vb):
    a = vas / vb
    k = math.sqrt(1 + a)
    return fs * k, qts * k

for vb in (10, 20, 40):
    fc, qtc = sealed(30, 0.35, 60, vb)
    print(f"{vb:>2} L: Fc={fc:5.1f} Hz,"
          f" Qtc={qtc:.2f}")
```

```
10 L: Fc= 79.4 Hz, Qtc=0.93
20 L: Fc= 60.0 Hz, Qtc=0.70
40 L: Fc= 47.4 Hz, Qtc=0.55
```

The 20 L box gives a near-Butterworth alignment (a Qtc of about 0.7) with a 60 Hz resonance. A smaller box gives higher, peakier bass; a bigger one lower, more damped bass. You can't get deep bass, high efficiency and a small box all at once: pick two.

(Filling the box with absorbent material can make it behave as if it were somewhat larger: Purdue's notes say up to about 15% in apparent volume, while also adding some effective moving mass.)

## Port tuning: Helmholtz intuition

A port behaves like the neck of a bottle. The air plug in the port is a mass bouncing on the springy air in the box. That is a **Helmholtz resonator**, and its resonance (the box tuning) is:

```formula
Fb = (c / (2 × π)) × √(A / (Vb × Leff))
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
Leff = Lp + k × r
where
Leff: the effective acoustic length of the port, in metres (m)
Lp: the physical length of the port tube, in metres (m)
k: the total end-correction factor for both ends (no unit): about 0.61 for an end that stops in free air, about 0.85 for an end flush with a flat panel; one of each gives about 1.46
r: the port's radius, in metres (m)
In words: add roughly one and a half port radii to the tube length when one end is flush with the baffle and the other is free inside the box.
```

Because the area is under the square root and divided by the length, a wider port must also be longer to keep the same Fb. Worked example: a 30 L box with a 5 cm diameter port, 15 cm long, with end corrections (k = 1.46):

```formula
A = π × (0.025 m)^2 ≈ 0.00196 m^2
Leff = 0.15 m + 1.46 × 0.025 m
Leff ≈ 0.1865 m
Vb × Leff = 0.03 m^3 × 0.1865 m
Vb × Leff ≈ 0.005595 m^4
Fb = (343 m/s / (2 × π))
     × √(0.00196 m^2 / 0.005595 m^4)
Fb ≈ 54.6 Hz × 0.592 ≈ 32.3 Hz
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

## Alignments, conceptually

The driver plus box is a **high-pass filter**: second-order for sealed, fourth-order for ported. An **alignment** is a choice of driver parameters, box volume and tuning that gives a particular filter shape, borrowed from electrical filter theory. Thiele (1961) and Small (1972–73) published tables of these; Butterworth (maximally flat), Chebyshev (some ripple, more extension) and quasi-Butterworth variants are common names. Modern practice is to simulate the response, excursion and port air speed in software, then measure.

## Cabinet resonance and bracing

The box's walls are panels that vibrate. If they resonate at frequencies the driver produces, the cabinet itself radiates sound, smearing and colouring the output. Remedies:

- **Stiff, dense material**: MDF and birch plywood are common choices.
- **Bracing**: internal struts or shelves that stiffen large panels, pushing their resonances higher and reducing their amplitude.
- **Damping**: lining or filling the box with absorbent material reduces internal standing waves between parallel walls and can damp panels.
- **Seal everything**: air leaks in a sealed box change its behaviour and can whistle.

> [!tip] If you build one
> Woodworking has its own hazards: control MDF dust with effective extraction and add suitable, correctly fitted respiratory protection where needed; a mask is not a substitute for extraction. Use power-tool guards and eye protection. Keep any amplifier electronics separate from the box-building and follow lesson 7's safety notes.

## Key takeaways
- A bare driver is a dipole: at low frequencies the rear wave cancels the front (acoustic short circuit). Baffles and boxes stop it.
- Baffle step: the move from half-space to full-space radiation costs up to 6 dB of on-axis level below a frequency set by baffle width.
- Sealed boxes roll off at 12 dB/octave; ported at 24 dB/octave with more output near Fb but poor cone control below it; open baffles add about 6 dB/octave of dipole loss to the driver response.
- Fs, Qts and Vas characterise a driver. In a sealed box, a smaller box raises both the resonance and the Q by the same factor; a Qtc of about 0.707 is maximally flat.
- Ports are Helmholtz resonators: the tuning rises with port area and falls with box volume and effective port length.
- Panels resonate: use stiff material, bracing and damping.

## Further reading
- [Loudspeaker enclosure — Wikipedia](https://en.wikipedia.org/wiki/Loudspeaker_enclosure)
- [Bass reflex — Wikipedia](https://en.wikipedia.org/wiki/Bass_reflex)
- [Thiele/Small parameters — Wikipedia](https://en.wikipedia.org/wiki/Thiele/Small_parameters)
- [Loudspeaker parameters (sealed-box Qtc, EBP) — D. G. Meyer, Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Wikipedia](https://en.wikipedia.org/wiki/Helmholtz_resonance)
- [Sound fields radiated by monopoles and dipoles — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
- [Transmission line loudspeaker — Wikipedia](https://en.wikipedia.org/wiki/Transmission_line_loudspeaker)
