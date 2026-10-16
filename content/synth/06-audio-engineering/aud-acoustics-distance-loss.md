---
id: aud-acoustics-distance-loss
title: Predict free-field distance loss
level: basic
minutes: 4
summary: Use the same direction and a source’s free-field far field.
sourceLesson: aud-acoustics
---

## The inverse square law

A small source in open space (a **free field**, with no reflections) spreads its power over the surface of a growing sphere. The area of a sphere grows with the square of its radius, so the same power is shared over more and more air:

```formula
I = P_ac / (4πr^2)
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
L_2 = L_1 − 20 log_10(r_2 / r_1)
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
ΔL = 20 log_10(2)
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

# The 1 m reference must be in the far
# field.
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
L_2 = 100 − 20 log_10(25 m / 1 m)
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
> - **Indoors**, reflections build a *reverberant field*. Beyond a certain distance (the critical distance) the level stops falling at 6 dB per doubling and levels off. The room-acoustics units cover rooms.
> - **Close to a source**, particularly a large one or a line of speakers, the level doesn't fall in neat inverse-square steps (see the later boundaries and fields unit).
> - **Acoustic line sources** (long columns of speakers) fall closer to 3 dB per doubling over part of their range, because the energy spreads over a cylinder rather than a sphere.

## Key takeaways
- Use the same direction and a source’s free-field far field.
- Each distance doubling reduces pressure level by about six decibels.
- Reflections, line-source geometry and near-field behaviour need different models.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
