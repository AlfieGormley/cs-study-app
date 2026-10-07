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

A current in a wire in a magnetic field feels a force. For the voice coil:

```
F = B * l * i
```

- **B** is the flux density in the gap (tesla).
- **l** is the length of wire in the field (metres).
- **i** is the current (amps).

Datasheets quote the product **Bl** ("BL") in T·m. A driver with Bl = 7 T·m and 1 A in the coil feels 7 N. Audio current alternates, so the force alternates and the cone moves back and forth, pushing air (lesson 1).

The cone, coil and the air it carries have **mass**; the suspension acts as a **spring**. Mass on a spring has a resonance. That's the driver's **free-air resonance, Fs**, one of the Thiele–Small parameters in lesson 5. Below Fs the output falls away.

A driver is also a **generator**: a moving coil in a field produces a voltage (back-EMF), exactly as a dynamic mic does. That back-EMF is why the impedance changes so much near resonance.

## Impedance: nominal vs reality

An "8 Ω" speaker isn't 8 Ω. Its impedance depends on frequency:

- At DC it's just the voice-coil resistance, **Re** (often around 5–7 Ω for an "8 Ω" driver).
- Near **Fs** it rises to a sharp peak, because the back-EMF of the resonating cone opposes the current.
- Above resonance it falls to a minimum, then rises again at high frequencies because the voice coil is an **inductor**.

Here's a simplified model of a small woofer, using the sample parameters from Purdue's loudspeaker notes (Re = 6.6 Ω, Le = 0.48 mH, Fs = 65 Hz, Qes = 0.436, Qms = 2.25):

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

**Nominal impedance** is a single rounded label for the region above resonance. The loudspeaker standard IEC 60268-5 says the minimum impedance in the rated frequency range should not fall below **80% of the rated (nominal) impedance**, so an 8 Ω speaker shouldn't dip below 6.4 Ω there. Not every manufacturer follows that rule, and real multi-way speakers with crossovers can dip well below their label, which is why amplifier makers care about the *minimum*, not the nominal (lesson 7).

## Sensitivity and the maths of power vs SPL

**Sensitivity** is the SPL on-axis at 1 m for a reference input. Two conventions:

- **dB SPL @ 1 W / 1 m.** One watt into the *nominal* impedance.
- **dB SPL @ 2.83 V / 1 m.** 2.83 V is 1 W into 8 Ω (2.83² / 8 ≈ 1.0 W).

Using nominal impedance to define the test voltage, the two references agree for 8 Ω. For **4 Ω**, 2.83 V corresponds to **2 W nominal**, making its voltage-sensitivity figure about **3 dB higher**. Actual electrical power varies with complex impedance and frequency; compare the measurement conditions.

For a fixed signal spectrum in the linear range, use this approximate on-axis free-field, far-field estimate (neglecting air absorption and power compression):

```
SPL = sensitivity + 10*log10(P / 1 W)
                  - 20*log10(r / 1 m)
```

Each **doubling of power adds only 3 dB**; ten times the power adds 10 dB.

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

Worked example (from Purdue's notes): you want 90 dB SPL at 4 m outdoors from an 86 dB/1 W/1 m speaker.

1. Distance loss: 20·log10(4) ≈ 12 dB, so you need 102 dB at 1 m.
2. That's 16 dB above the 1 W figure.
3. Power: 10^(16/10) ≈ **40 W**, before any headroom for peaks.

Every 3 dB of sensitivity halves the amplifier power needed for the same level. Sensitivity is closely related to **efficiency** (acoustic power out ÷ electrical power in), which is low: only around 1% for a typical home loudspeaker. The rest becomes heat, mostly in the voice coil.

## Frequency response

A frequency response plot shows on-axis SPL (at a fixed input) against frequency. Look for:

- The **usable range**, often given as ±3 dB limits, with the low-frequency limit set mainly by Fs and the enclosure.
- **Smoothness**: narrow peaks often come from cone breakup or cabinet resonance.
- **Off-axis curves**: how the response changes at 30° or 60°. Because of diffraction, a driver radiates widely when its wavelength is large compared with the cone, and **beams** (narrows its dispersion) when the wavelength becomes comparable with the cone. For a piston of radius *a*, directivity becomes significant around ka = 1, i.e. f ≈ c / (2πa): about 840 Hz for a woofer with a 13 cm effective diameter, and about 4.4 kHz for a 25 mm tweeter dome.

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
- A moving-coil driver produces force F = Bl·i on the voice coil; the suspension and moving mass create a resonance, Fs.
- Impedance varies with frequency: Re at DC, a peak at Fs, a minimum above it, and a rise from coil inductance. IEC 60268-5 expects the in-band minimum to be at least 80% of the nominal rating.
- Sensitivity is SPL at 1 m for 1 W or 2.83 V; for a 4 Ω speaker the 2.83 V figure is 3 dB higher.
- SPL = sensitivity + 10·log10(P) − 20·log10(r): doubling power gives only +3 dB.
- Power handling has thermal and excursion limits; drivers beam above roughly f = c/(2πa) and break up at higher frequencies.

## Further reading
- [Loudspeaker — Wikipedia](https://en.wikipedia.org/wiki/Loudspeaker)
- [Loudspeaker basics — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Audio/spk.html)
- [Electrodynamic speaker driver — Wikipedia](https://en.wikipedia.org/wiki/Electrodynamic_speaker_driver)
- [Nominal impedance (loudspeakers) — Wikipedia](https://en.wikipedia.org/wiki/Nominal_impedance)
- [Loudspeaker parameters (lecture notes) — D. G. Meyer, Purdue University](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [What is impedance? (IEC 60268-5 80% rule) — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
- [Compression driver — Wikipedia](https://en.wikipedia.org/wiki/Compression_driver)
