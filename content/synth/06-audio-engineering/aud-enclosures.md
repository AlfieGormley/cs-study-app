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

Even in a box, the front baffle has a finite size. At high frequencies, where the baffle is large compared with the wavelength, the driver radiates into the **half-space** in front (2π steradians). At low frequencies, where the wavelength is much larger than the baffle, sound wraps round the cabinet and radiates into the **full space** (4π).

For the same cone motion, radiating into half-space gives twice the sound pressure of full space (the baffle acts like a mirror, adding a coherent "image" source): **+6 dB**. So as frequency falls and the radiation spreads into full space, on-axis level drops by up to **6 dB**. So a speaker's on-axis response steps down by up to 6 dB going from high to low frequencies. The transition happens where the wavelength is comparable with the baffle width: a few hundred hertz for a typical bookshelf speaker.

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

The rear wave travels down a long, folded, damped duct before leaving through a vent. The line length is typically chosen as a **quarter wavelength** at the lowest frequency the design targets (often near the driver's resonance), so the line's output reinforces the front at low frequencies while the damping absorbs higher frequencies. They're more complex to design and build, and benefit from modelling software.

| Type | Roll-off | Trade-off |
|---|---|---|
| Sealed | 12 dB/oct | Compact, controlled |
| Ported | 24 dB/oct | More output; excursion below Fb |
| Open baffle | Additional ~6 dB/oct dipole loss | Driver roll-off also contributes |
| Transmission line | varies | Complex build |

## Thiele–Small parameters

A driver datasheet lists **Thiele–Small (T/S) parameters**, measured at low levels where the driver behaves linearly. The three you use most:

- **Fs**: the free-air resonance (moving mass on the suspension spring).
- **Qts**: the total Q at Fs: how damped the resonance is. It combines the mechanical Q (Qms, losses in the suspension) and the electrical Q (Qes, damping from the motor and amplifier): Qts = Qms·Qes / (Qms + Qes). Purdue's notes put most drivers between about 0.2 and 0.5.
- **Vas**: the volume of air with the same springiness (compliance) as the driver's suspension. For a fixed effective cone area, larger Vas means a softer suspension. Vas also depends on cone area squared, so it is not a suspension-stiffness comparison across arbitrary driver sizes.

A rough rule of thumb using the **efficiency bandwidth product**, EBP = Fs / Qes: drivers around 50 tend to suit sealed boxes, around 100 ported. It's a starting point, not a design method.

Manufacturing tolerances are loose: Purdue's notes give typical factory tolerances of about ±15% for Fs and ±20–30% for Vas. Measure your own driver if accuracy matters.

### The sealed-box equations

Put a driver in a sealed box of volume Vb. The box air adds stiffness in proportion to the **compliance ratio** α = Vas / Vb. Resonance frequency and Q both scale with the square root of total stiffness, giving the closed-box results:

```
alpha = Vas / Vb
Fc  = Fs  * sqrt(1 + alpha)
Qtc = Qts * sqrt(1 + alpha)
```

**Qtc** sets the shape of the bass roll-off:

| Qtc | Behaviour |
|---|---|
| 0.5 | Critically damped, −6 dB at Fc |
| 0.707 | Butterworth: maximally flat, −3 dB at Fc |
| ~1.0–1.1 | Peak before roll-off, "boomier" |

Worked example: a driver with Fs = 30 Hz, Qts = 0.35, Vas = 60 L.

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

The 20 L box gives a near-Butterworth alignment (Qtc ≈ 0.7) with Fc = 60 Hz. A smaller box gives higher, peakier bass; a bigger one lower, more damped bass. You can't get deep bass, high efficiency and a small box all at once: pick two.

(These equations ignore box losses and stuffing. Filling the box with absorbent material can make it behave as if it were somewhat larger: Purdue's notes say up to about 15% in apparent volume, while also adding some effective moving mass.)

## Port tuning: Helmholtz intuition

A port behaves like the neck of a bottle. The air plug in the port is a mass bouncing on the springy air in the box:

```
Fb = (c / (2*pi)) * sqrt(A / (Vb * Leff))
```

- **A** is the port's cross-section area, **Vb** the box volume, and **Leff** the port's *effective* length: its physical length plus an **end correction** for each open end (roughly 0.6 to 0.85 times the port radius per end, depending on how the end is flanged).
- Bigger box or longer port → lower tuning. Wider port → higher tuning, so a wider port must also be longer for the same Fb.

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
- Fs, Qts and Vas characterise a driver; in a sealed box α = Vas/Vb, Fc = Fs·√(1+α), Qtc = Qts·√(1+α); Qtc ≈ 0.707 is maximally flat.
- Ports are Helmholtz resonators: Fb rises with port area and falls with box volume and effective port length.
- Panels resonate: use stiff material, bracing and damping.

## Further reading
- [Loudspeaker enclosure — Wikipedia](https://en.wikipedia.org/wiki/Loudspeaker_enclosure)
- [Bass reflex — Wikipedia](https://en.wikipedia.org/wiki/Bass_reflex)
- [Thiele/Small parameters — Wikipedia](https://en.wikipedia.org/wiki/Thiele/Small_parameters)
- [Loudspeaker parameters (sealed-box Qtc, EBP) — D. G. Meyer, Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Wikipedia](https://en.wikipedia.org/wiki/Helmholtz_resonance)
- [Sound fields radiated by monopoles and dipoles — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
- [Transmission line loudspeaker — Wikipedia](https://en.wikipedia.org/wiki/Transmission_line_loudspeaker)
