---
id: aud-acoustics
title: Acoustics and sound in air
level: basic
minutes: 14
summary: Sound as pressure waves, the speed of sound and wavelength, dB SPL with its 20 µPa reference, the inverse square law with worked maths, adding incoherent sources, and how reflection, absorption and diffraction depend on wavelength.
---

Everything in this module happens in air. Your synth makes a voltage; a loudspeaker turns it into moving air; a room bounces it about; an ear or a microphone turns it back into something useful. Before looking at any of those devices, you need a working model of what sound in air actually is and how it behaves with distance.

Module 1 covered decibels as ratios and dBFS, and module 5 covered dBu and dBV for signal voltages. This lesson adds the decibel scale for *sound in air*: dB SPL.

## Sound is a pressure wave

A loudspeaker cone moving forward squashes the air in front of it slightly (a **compression**); moving back, it leaves the air slightly thinner (a **rarefaction**). Each layer of air pushes on the next, so the disturbance travels outward. The air molecules themselves only jiggle back and forth around where they started. What travels is the *pattern* of pressure.

```diagram
 cone   compression   rarefaction
  |  ||||||||    |   |   |   |||||||
  |  ||||||||    |   |   |   |||||||
  ---------> direction of travel
```

Two consequences matter for audio engineering:

- Sound is **longitudinal**: the air moves along the direction of travel, not across it.
- The pressure changes are **tiny**. Atmospheric pressure is about 101,325 Pa. A painfully loud sound changes it by tens of pascals; a quiet one by thousandths of a pascal.

## Speed of sound and wavelength

In dry air the speed of sound depends mainly on temperature. A standard ideal-gas approximation is:

```
c = 331.3 * sqrt(1 + T / 273.15)   m/s
(T in degrees Celsius)
```

```python
import math

def c_air(t_c):
    return 331.3 * math.sqrt(
        1 + t_c / 273.15)

for t in (0, 20, 30):
    print(f"{t:>2} C: {c_air(t):.1f} m/s")
```

```
 0 C: 331.3 m/s
20 C: 343.2 m/s
30 C: 349.0 m/s
```

The usual working figure is **343 m/s at 20 °C**, which is about 1 metre every 2.9 ms. That number turns up everywhere: speaker delay times, room modes, crossover alignment.

**Wavelength** is how far the wave travels in one cycle:

```
lambda = c / f
```

| Frequency | Wavelength (c = 343 m/s) |
|---|---|
| 20 Hz | 17.15 m |
| 100 Hz | 3.43 m |
| 1 kHz | 34.3 cm |
| 10 kHz | 3.43 cm |
| 20 kHz | 1.7 cm |

Audible wavelengths span a factor of 1,000, from longer than a house to shorter than your thumb. Relative size strongly affects diffraction and scattering. Reflection and absorption also depend on material impedance, construction, mounting and incidence angle.

## Sound pressure level: dB SPL

Sound pressure is measured in pascals (Pa), as an RMS value. Because the range is so huge, we use decibels relative to a reference of **20 µPa**, roughly the quietest 1 kHz tone a young, healthy listener can detect:

```
L_p = 20 * log10(p / 20e-6)   dB SPL
```

It's `20·log10` because pressure is a field quantity, like voltage (module 1 explains why).

```python
import math

def spl(p_pa):
    return 20 * math.log10(p_pa / 20e-6)

for p in (20e-6, 0.02, 1.0, 20.0):
    print(f"{p:>8} Pa = "
          f"{spl(p):6.2f} dB SPL")
```

```
   2e-05 Pa =   0.00 dB SPL
    0.02 Pa =  60.00 dB SPL
     1.0 Pa =  93.98 dB SPL
    20.0 Pa = 120.00 dB SPL
```

Remember **1 Pa ≈ 94 dB SPL**. Microphone sensitivities are quoted at 1 Pa (lesson 3) and calibrators often produce 94 dB SPL for exactly this reason.

## The inverse square law

A small source in open space (a **free field**, with no reflections) spreads its power over the surface of a growing sphere, of area 4πr². So intensity falls as 1/r², and pressure as 1/r:

```
L(r2) = L(r1) - 20 * log10(r2 / r1)
```

Each **doubling of distance** loses 20·log10(2) = **6.02 dB**, usually rounded to 6 dB.

```python
import math

L1 = 100.0  # dB SPL at 1 m
for r in (1, 2, 4, 8, 10, 25):
    L = L1 - 20 * math.log10(r / 1)
    print(f"{r:>2} m: {L:6.2f} dB SPL")
```

```
 1 m: 100.00 dB SPL
 2 m:  93.98 dB SPL
 4 m:  87.96 dB SPL
 8 m:  81.94 dB SPL
10 m:  80.00 dB SPL
25 m:  72.04 dB SPL
```

Worked example: a speaker gives 100 dB SPL at 1 m. A listener at 25 m gets 100 − 20·log10(25) = 100 − 27.96 ≈ **72 dB SPL**. Ten times the distance costs 20 dB.

> [!warning] Where the law doesn't hold
> - **Indoors**, reflections build a *reverberant field*. Beyond a certain distance (the critical distance) the level stops falling at 6 dB per doubling and levels off. Lesson 9 covers rooms.
> - **Close to a source**, particularly a large one or a line of speakers, the level doesn't follow a neat 1/r law (see near field below).
> - **Line sources** (long columns of speakers) fall closer to 3 dB per doubling over part of their range, because the energy spreads over a cylinder rather than a sphere.

## Adding sources

Independent sound sources (for example unrelated noise sources) can be treated as **incoherent** over the averaging interval: their waveforms are unrelated, so their *powers* add, not their pressures:

```
L_total = 10 * log10(sum(10 ** (L_i / 10)))
```

```python
import math

def lsum(*levels):
    return 10 * math.log10(
        sum(10 ** (l / 10) for l in levels))

print(round(lsum(90, 90), 2))
print(round(lsum(90, 80), 2))
print(round(lsum(90, 90, 90, 90), 2))
```

```
93.01
90.41
96.02
```

- Two equal incoherent sources: **+3 dB**.
- A source 10 dB quieter adds only about 0.4 dB. The loud one dominates.
- Four equal sources: +6 dB.

**Coherent** sources are different. Two speakers playing the *same* signal at the same distance add in pressure, so they can give up to **+6 dB** where they arrive in phase, and deep cancellation where they arrive out of phase. For delayed broadband copies, the repeating frequency peaks and notches are **comb filtering**; a single tone instead shows spatial interference, and it is why lesson 3's 3:1 rule and lesson 6's driver alignment exist.

## Reflection, absorption and diffraction

At a boundary, sound can be reflected, transmitted or absorbed; diffraction describes spreading around edges and openings. Wavelength, impedance and construction all matter.

**Reflection.** A hard, large, flat surface (a wall, a desk, a window) reflects sound like a mirror reflects light: angle in equals angle out. This only works well when the surface is large compared with the wavelength. A 30 cm panel is a good mirror at 10 kHz (λ = 3.4 cm) but almost invisible at 100 Hz (λ = 3.4 m).

**Absorption.** Porous materials (mineral wool, thick fabric) turn some of the sound's energy into heat. Each material has an **absorption coefficient** α between 0 (perfect reflector) and 1 (absorbs everything), which varies with frequency. Thin foam absorbs high frequencies well and does almost nothing to bass, because bass wavelengths are far longer than the foam is thick.

**Diffraction.** Waves bend around obstacles and spread out through openings. When an obstacle is small compared with the wavelength, sound wraps around it with hardly a shadow. When it's large, it casts an acoustic shadow. This is why you can hear the bass, but not the cymbals, from a band round the corner; why your head shadows high frequencies but not low ones (lesson 2); and why a loudspeaker radiates almost equally in all directions at low frequencies but beams forward at high frequencies (lesson 4).

| Size vs wavelength | Behaviour |
|---|---|
| Object much smaller | Sound diffracts round it |
| Comparable | Partial, frequency-dependent |
| Object much larger | Reflection and shadowing |

## Near field and far field

Very close to a source, the sound field is complicated: different parts of the source (the cone, the edges of the cabinet, several drivers) are at noticeably different distances from you, and their contributions interfere. Level can change sharply as you move a few centimetres, and it doesn't follow 1/r.

Further away, in the **far field**, the source behaves like a point: level falls 6 dB per doubling, and the balance between drivers settles down. The distance needed depends on source geometry, frequency and the measurement criterion. Several source dimensions alone is not a universal far-field test for a large array; follow the manufacturer's measurement method and verify that distance-scaled responses converge. Datasheet figures are quoted "at 1 m", but large speakers are often measured further away and the result scaled back to 1 m with the inverse square law.

> [!tip] "Near-field monitor" means something else
> Studio "near-field monitors" are small speakers listened to from about 1–2 m, so that you hear more direct sound than room reflections. They aren't about the acoustic near field of the speaker itself. Lesson 9 covers them.

## Key takeaways
- Sound is a longitudinal pressure wave; the pressure changes are tiny compared with atmospheric pressure.
- c ≈ 343 m/s at 20 °C; λ = c/f, from about 17 m at 20 Hz to 1.7 cm at 20 kHz.
- dB SPL = 20·log10(p / 20 µPa); 1 Pa ≈ 94 dB SPL.
- In a free field, level falls 6.02 dB per doubling of distance (20·log10 of the distance ratio). Rooms, line arrays and the near field break this.
- Incoherent sources add in power (two equal ones give +3 dB); coherent copies add in pressure (up to +6 dB, or cancel).
- Whether sound reflects, is absorbed or diffracts depends on object size compared with the wavelength.

## Further reading
- [Speed of sound — HyperPhysics (Georgia State University)](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law for sound — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
- [Sound intensity and decibels — HyperPhysics](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Sound pressure — Wikipedia](https://en.wikipedia.org/wiki/Sound_pressure)
- [Inverse-square law — Wikipedia](https://en.wikipedia.org/wiki/Inverse-square_law)
- [Longitudinal and transverse wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Diffraction — Wikipedia](https://en.wikipedia.org/wiki/Diffraction)
