---
id: aud-acoustics
title: Acoustics and sound in air
level: basic
minutes: 18
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

In dry air the speed of sound depends mainly on temperature: warmer air molecules move faster, so they pass the disturbance on faster. Pressure and (to a small degree) humidity barely matter. A standard ideal-gas approximation, good for everyday air temperatures, is:

```formula
c = 331.3 × √(1 + T / 273.15)
where
c: the speed of sound in dry air, in metres per second (m/s)
T: the air temperature, in degrees Celsius (°C); everyday values are about 0–35 °C
331.3: the speed of sound in dry air at 0 °C, in m/s
273.15: the number you add to a Celsius temperature to get kelvin (absolute temperature), so 1 + T / 273.15 is the absolute temperature divided by that of 0 °C
√: square root: the number that, multiplied by itself, gives what is inside the brackets
In words: the speed of sound grows with the square root of the absolute temperature, which works out at roughly 0.6 m/s faster for every 1 °C warmer near room temperature.
```

Worked example at a room temperature of 20 °C:

```formula
c = 331.3 × √(1 + 20 / 273.15)
c = 331.3 × √(1.0732)
c = 331.3 × 1.0359
c ≈ 343.2 m/s
where
c: the speed of sound in dry air, in metres per second (m/s)
√: square root
≈: approximately equal to (the result is rounded)
m: metres
s: seconds
In words: at 20 °C sound travels about 343 metres every second.
```

The approximation assumes dry air behaving as an ideal gas. Humidity raises the speed by a fraction of a percent, which rarely matters in practice. The same calculation as a short program:

```python
import math

def c_air(t_c):
    return 331.3 * math.sqrt(
        1 + t_c / 273.15)

for t in (0, 20, 30):
    print(f"{t:>2} C: {c_air(t):.1f} m/s")
```

```output
 0 C: 331.3 m/s
20 C: 343.2 m/s
30 C: 349.0 m/s
```

The usual working figure is **343 m/s at 20 °C**, which is about 1 metre every 2.9 ms. That number turns up everywhere: speaker delay times, room modes, crossover alignment.

**Wavelength** is how far the wave travels in one cycle. In one second the wave travels about 343 metres and completes as many cycles as its frequency, so each cycle covers the speed divided by the frequency:

```formula
λ = c / f
where
λ: lambda, the wavelength: the distance the wave travels during one cycle, in metres (m)
c: the speed of sound, about 343 metres per second (m/s) at 20 °C
f: the frequency of the sound, in hertz (Hz)
Hz: hertz, the unit of frequency: one cycle per second
In words: the wavelength is the speed of sound divided by the frequency, so doubling the frequency halves the wavelength.
```

Worked example for a 1 kHz tone (1000 Hz):

```formula
λ = 343 m/s / 1000 Hz
λ = 0.343 m
where
λ: lambda, the wavelength, in metres (m)
m/s: metres per second, the unit of speed
m: metres
s: seconds
Hz: hertz, cycles per second
In words: a 1 kHz tone has a wavelength of about 34 cm.
```

The same division gives the table below. It applies to any wave, as long as you use the speed for the medium the wave is in (sound in water travels about four times faster, so its wavelengths are four times longer).

| Frequency | Wavelength (at 343 m/s) |
|---|---|
| 20 Hz | 17.15 m |
| 100 Hz | 3.43 m |
| 1 kHz | 34.3 cm |
| 10 kHz | 3.43 cm |
| 20 kHz | 1.7 cm |

Audible wavelengths span a factor of 1,000, from longer than a house to shorter than your thumb. Relative size strongly affects diffraction and scattering. Reflection and absorption also depend on material impedance, construction, mounting and incidence angle.

## Sound pressure level: dB SPL

Sound pressure is measured in pascals (Pa), as an RMS value (a kind of average size of a wave that swings both ways). Because the range is so huge, we use decibels relative to a reference of **20 µPa** (20 millionths of a pascal), roughly the quietest 1 kHz tone a young, healthy listener can detect. The sound pressure level is:

```formula
L_p = 20 × log_10(p / p_0)
p_0 = 20 µPa = 0.00002 Pa
where
L_p: the sound pressure level, in decibels relative to 20 µPa (dB SPL)
p: the RMS sound pressure you measure, in pascals (Pa)
p_0: the reference pressure, 20 µPa, which is defined to be 0 dB SPL
log_10: the base-10 logarithm: the power you must raise 10 to in order to get the number, e.g. log_10(1000) = 3
µ: micro, meaning one millionth (0.000001)
Pa: pascal, the unit of pressure: one newton of force per square metre
In words: count how many times bigger than 20 µPa the pressure is, take the base-10 logarithm and multiply by 20; every tenfold increase in pressure adds 20 dB.
```

The multiplier is 20, not 10, because pressure is a field quantity, like voltage: the power a sound carries is proportional to pressure squared, and squaring a ratio doubles its logarithm (module 1 explains why). Worked example for a pressure of 1 Pa:

```formula
L_p = 20 × log_10(1 Pa / 0.00002 Pa)
L_p = 20 × log_10(50000)
L_p = 20 × 4.699
L_p ≈ 93.98 dB SPL
where
L_p: the sound pressure level, in dB SPL
log_10: the base-10 logarithm
Pa: pascal, the unit of pressure
dB: decibel, a tenth of a bel: a logarithmic way of expressing a ratio
SPL: sound pressure level, meaning the decibel figure is relative to 20 µPa
≈: approximately equal to
In words: a sound pressure of 1 pascal is about 94 dB SPL.
```

As a program, for a few pressures:

```python
import math

def spl(p_pa):
    return 20 * math.log10(p_pa / 20e-6)

for p in (20e-6, 0.02, 1.0, 20.0):
    print(f"{p:>8} Pa = "
          f"{spl(p):6.2f} dB SPL")
```

```output
   2e-05 Pa =   0.00 dB SPL
    0.02 Pa =  60.00 dB SPL
     1.0 Pa =  93.98 dB SPL
    20.0 Pa = 120.00 dB SPL
```

Remember **1 Pa ≈ 94 dB SPL**. Microphone sensitivities are quoted at 1 Pa (lesson 3) and calibrators often produce 94 dB SPL for exactly this reason.

## The inverse square law

A small source in open space (a **free field**, with no reflections) spreads its power over the surface of a growing sphere. The area of a sphere grows with the square of its radius, so the same power is shared over more and more air:

```formula
I = P_ac / (4 × π × r^2)
p ∝ 1 / r
where
I: the sound intensity: the acoustic power passing through each square metre, in watts per square metre (W/m²)
P_ac: the acoustic power the source radiates, in watts (W); this is sound power, not the amplifier's electrical power
π: pi, the ratio of a circle's circumference to its diameter, about 3.14159
r: the distance from the source, in metres (m)
p: the RMS sound pressure at distance r, in pascals (Pa)
∝: "is proportional to": when one side is multiplied by some factor, the other is multiplied by the same factor
In words: 4 × π × r² is the area of a sphere of radius r, so intensity falls with the square of distance. Intensity is proportional to pressure squared, so pressure falls in proportion to 1/r: double the distance and the intensity quarters while the pressure halves.
```

This is the **inverse square law**. Turning the pressure ratio into decibels (20 × log, because pressure is a field quantity) gives the working form, which predicts the level at one distance from a level measured at another:

```formula
L_2 = L_1 − 20 × log_10(r_2 / r_1)
where
L_1: the measured level at distance r_1, in dB SPL
L_2: the predicted level at distance r_2, in dB SPL
r_1: the distance where you know the level, in metres (m)
r_2: the distance you want the level at, in metres (m)
log_10: the base-10 logarithm
In words: the level falls by 20 times the logarithm of the distance ratio, so it depends only on how many times further away you are, not on the distance in metres.
```

Each **doubling of distance** therefore loses the same amount:

```formula
ΔL = 20 × log_10(2)
ΔL = 20 × 0.30103
ΔL ≈ 6.02 dB
where
ΔL: the drop in level for a doubling of distance, in decibels (dB); Δ (delta) means "change in"
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to
In words: in a free field, every doubling of distance costs about 6 dB, usually rounded to 6 dB.
```

```python
import math

L1 = 100.0  # dB SPL at 1 m
for r in (1, 2, 4, 8, 10, 25):
    L = L1 - 20 * math.log10(r / 1)
    print(f"{r:>2} m: {L:6.2f} dB SPL")
```

```output
 1 m: 100.00 dB SPL
 2 m:  93.98 dB SPL
 4 m:  87.96 dB SPL
 8 m:  81.94 dB SPL
10 m:  80.00 dB SPL
25 m:  72.04 dB SPL
```

Worked example: a speaker gives 100 dB SPL at 1 m. What does a listener at 25 m get?

```formula
L_2 = 100 − 20 × log_10(25 m / 1 m)
L_2 = 100 − 20 × 1.398
L_2 = 100 − 27.96
L_2 ≈ 72 dB SPL
where
L_2: the level at 25 m, in dB SPL
log_10: the base-10 logarithm
m: metres
dB: decibels
SPL: sound pressure level (relative to 20 µPa)
≈: approximately equal to
In words: 25 times further away loses about 28 dB, leaving about 72 dB SPL. Ten times the distance would cost exactly 20 dB.
```

> [!warning] Where the law doesn't hold
> - **Indoors**, reflections build a *reverberant field*. Beyond a certain distance (the critical distance) the level stops falling at 6 dB per doubling and levels off. Lesson 9 covers rooms.
> - **Close to a source**, particularly a large one or a line of speakers, the level doesn't fall in neat inverse-square steps (see near field below).
> - **Line sources** (long columns of speakers) fall closer to 3 dB per doubling over part of their range, because the energy spreads over a cylinder rather than a sphere.

## Adding sources

Independent sound sources (for example unrelated noise sources) can be treated as **incoherent** over the averaging interval: their waveforms are unrelated, so their *powers* add, not their pressures. To add levels, turn each one back into a relative power, add the powers, and turn the total back into decibels:

```formula
L_total = 10 × log_10(Σ 10^{L_i / 10})
where
L_total: the combined level at the listening position, in dB SPL
L_i: the level of source number i on its own, at the same position, in dB SPL
i: a counter that runs over the sources: 1, 2, 3 and so on
10^{L_i / 10}: the relative power of source i (10 raised to the power of its level divided by 10)
Σ: sigma, "sum of": add up the term for every source
log_10: the base-10 logarithm
In words: convert each level to a power, add the powers, and convert back to decibels with 10 × log because these are powers, not pressures.
```

Worked example, two equal 90 dB SPL sources, then a 90 and an 80:

```formula
L_total = 10 × log_10(10^9 + 10^9)
L_total = 10 × log_10(2 × 10^9)
L_total = 10 × 9.301 ≈ 93.01 dB SPL
L_mix = 10 × log_10(10^9 + 10^8)
L_mix = 10 × log_10(1.1 × 10^9)
L_mix = 10 × 9.0414 ≈ 90.41 dB SPL
where
L_total: the combined level of two 90 dB SPL sources, in dB SPL
L_mix: the combined level of a 90 dB SPL and an 80 dB SPL source, in dB SPL
log_10: the base-10 logarithm
10^9: the relative power of a 90 dB source (10 to the power 90 / 10)
10^8: the relative power of an 80 dB source
dB: decibels
SPL: sound pressure level
≈: approximately equal to
In words: two equal unrelated sources give 3 dB more than one; adding a source 10 dB quieter raises the total by only about 0.4 dB.
```

This assumes the sources really are unrelated and you average over a long enough time. The same sum as a program:

```python
import math

def lsum(*levels):
    return 10 * math.log10(
        sum(10 ** (l / 10) for l in levels))

print(round(lsum(90, 90), 2))
print(round(lsum(90, 80), 2))
print(round(lsum(90, 90, 90, 90), 2))
```

```output
93.01
90.41
96.02
```

- Two equal incoherent sources: **+3 dB**.
- A source 10 dB quieter adds only about 0.4 dB. The loud one dominates.
- Four equal sources: +6 dB.

**Coherent** sources are different. Two speakers playing the *same* signal at the same distance add in pressure, so they can give up to **+6 dB** where they arrive in phase, and deep cancellation where they arrive out of phase. Compare doubling the pressure with doubling the power:

```formula
ΔL_coh = 20 × log_10(2) ≈ +6.02 dB
ΔL_inc = 10 × log_10(2) ≈ +3.01 dB
where
ΔL_coh: the gain from adding a second, identical, in-phase copy (pressure doubles), in decibels (dB)
ΔL_inc: the gain from adding a second, equal but unrelated source (power doubles), in decibels (dB)
Δ: delta, "change in"
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibels
In words: two identical in-phase copies double the pressure (+6 dB); two equal unrelated sources double the power (+3 dB).
```
 For delayed broadband copies, the repeating frequency peaks and notches are **comb filtering**; a single tone instead shows spatial interference, and it is why lesson 3's 3:1 rule and lesson 6's driver alignment exist.

## Reflection, absorption and diffraction

At a boundary, sound can be reflected, transmitted or absorbed; diffraction describes spreading around edges and openings. Wavelength, impedance and construction all matter.

**Reflection.** A hard, large, flat surface (a wall, a desk, a window) reflects sound like a mirror reflects light: angle in equals angle out. This only works well when the surface is large compared with the wavelength. A 30 cm panel is a good mirror at 10 kHz (wavelength 3.4 cm) but almost invisible at 100 Hz (wavelength 3.4 m).

**Absorption.** Porous materials (mineral wool, thick fabric) turn some of the sound's energy into heat. Each material has an **absorption coefficient**, the fraction of arriving sound energy that is not reflected back:

```formula
α = 1 − E_ref / E_inc
where
α: alpha, the absorption coefficient of the surface; it has no unit and lies between 0 and 1
E_ref: the sound energy reflected back from the surface
E_inc: the sound energy arriving at (incident on) the surface
In words: the absorption coefficient is the share of the sound that does not come back. 0 means a perfect reflector, 1 means nothing returns (as from an open window).
```

For example, a panel that reflects 30 % of the arriving energy has an absorption coefficient of 0.7. The coefficient varies with frequency, so it is quoted per octave band. Thin foam absorbs high frequencies well and does almost nothing to bass, because bass wavelengths are far longer than the foam is thick.

**Diffraction.** Waves bend around obstacles and spread out through openings. When an obstacle is small compared with the wavelength, sound wraps around it with hardly a shadow. When it's large, it casts an acoustic shadow. This is why you can hear the bass, but not the cymbals, from a band round the corner; why your head shadows high frequencies but not low ones (lesson 2); and why a loudspeaker radiates almost equally in all directions at low frequencies but beams forward at high frequencies (lesson 4).

| Size vs wavelength | Behaviour |
|---|---|
| Object much smaller | Sound diffracts round it |
| Comparable | Partial, frequency-dependent |
| Object much larger | Reflection and shadowing |

## Near field and far field

Very close to a source, the sound field is complicated: different parts of the source (the cone, the edges of the cabinet, several drivers) are at noticeably different distances from you, and their contributions interfere. Level can change sharply as you move a few centimetres, and it doesn't follow the inverse square law.

Further away, in the **far field**, the source behaves like a point: level falls 6 dB per doubling, and the balance between drivers settles down. The distance needed depends on source geometry, frequency and the measurement criterion. Several source dimensions alone is not a universal far-field test for a large array; follow the manufacturer's measurement method and verify that distance-scaled responses converge. Datasheet figures are quoted "at 1 m", but large speakers are often measured further away and the result scaled back to 1 m with the inverse square law.

> [!tip] "Near-field monitor" means something else
> Studio "near-field monitors" are small speakers listened to from about 1–2 m, so that you hear more direct sound than room reflections. They aren't about the acoustic near field of the speaker itself. Lesson 9 covers them.

## Key takeaways
- Sound is a longitudinal pressure wave; the pressure changes are tiny compared with atmospheric pressure.
- Sound travels at about 343 m/s at 20 °C. Wavelength is speed divided by frequency, from about 17 m at 20 Hz to 1.7 cm at 20 kHz.
- dB SPL is 20 times the base-10 logarithm of the pressure divided by 20 µPa; 1 Pa ≈ 94 dB SPL.
- In a free field, level falls 6.02 dB per doubling of distance (20 times the logarithm of the distance ratio). Rooms, line arrays and the near field break this.
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
