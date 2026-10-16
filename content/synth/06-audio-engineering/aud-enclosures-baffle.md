---
id: aud-enclosures-baffle
title: Separate front and rear radiation
level: intermediate
minutes: 4
summary: A bare driver has dipole cancellation at low frequencies.
sourceLesson: aud-enclosures
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

Even in a box, the front baffle has a finite size. At high frequencies, where the baffle is large compared with the wavelength, the driver radiates into the **half-space** in front: half a sphere of directions. At low frequencies, where the wavelength is much larger than the baffle, sound diffracts around the cabinet and radiates into the **full space**: the whole sphere.

Engineers often call these "2π" and "4π" radiation, after the solid angle each one covers:

```formula
Ω_full = 4π sr
Ω_half = 2π sr
where
Ω_full: the solid angle of a whole sphere, which a driver fills when it radiates in all directions (full space)
Ω_half: the solid angle of half a sphere, which a driver on a large flat baffle fills (half-space)
π: pi, the ratio of a circle's circumference to its diameter, about 3.14159
sr: steradian, the unit of solid angle: how much of the space around a point a cone of directions covers
In words: half-space is exactly half of all possible directions, so "2π" means "in front of a big wall" and "4π" means "floating in free space".
```

For the same cone motion, radiating into half-space gives twice the sound pressure of full space: the baffle acts like a mirror, adding a coherent "image" source. Doubling pressure is a 6 dB rise, because sound pressure level is 20 times the base-10 logarithm of a pressure ratio:

```formula
ΔL = 20 log_10(p_half / p_full)
ΔL = 20 log_10(2)
ΔL ≈ 6.02 dB
where
ΔL: the difference in on-axis level between half-space and full-space radiation, in decibels (dB)
p_half: the on-axis sound pressure for fixed cone volume velocity when radiating into ideal half-space, in pascals (Pa)
p_full: the on-axis sound pressure for the same cone motion in full space, in pascals (Pa); here p_half = 2 × p_full
log_10: the base-10 logarithm: log_10(x) is the power you raise 10 to in order to get x; log_10(2) ≈ 0.301
≈: approximately equal to
dB: decibel, a logarithmic unit for comparing two levels
In words: twice the pressure is about 6 dB louder, so losing the baffle's mirror effect costs about 6 dB.
```

So as frequency falls and the radiation spreads into full space, a speaker's on-axis response steps down by up to **6 dB** going from high to low frequencies. The transition happens where the wavelength is comparable with the baffle width: a few hundred hertz for a typical bookshelf speaker. This is the ideal figure: the real step is smoother, and nearby walls and floors change it.

Designers compensate with **baffle step compensation**: usually a gentle shelf in the crossover that reduces everything above the step. In a real room, placing the speaker near a wall gives back some of the lost bass, which is why compensation is a judgement call.

## Key takeaways
- A bare driver has dipole cancellation at low frequencies.
- A baffle separates the front and rear paths.
- For fixed cone motion, a finite baffle can produce an approximately six-decibel transition; boundary placement changes it.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Helmholtz resonance — Joe Wolfe, UNSW](https://phys.unsw.edu.au/jw/Helmholtz.html)
- [Monopole and dipole radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/rad2/mdq.html)
