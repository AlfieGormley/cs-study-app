---
id: aud-enclosures-baffle
title: Separate front and rear radiation
level: intermediate
minutes: 4
summary: A bare driver has dipole cancellation at low frequencies.
sourceLesson: aud-enclosures
---

Hold a bare woofer in the air, play a bass line through it, and you get a thin, tinny sound. Mount the same driver in a box and the bass appears. This lesson explains why, and how the box's design shapes the bass response.

It's a deep subject with decades of published theory. The goal here is the concepts you need to read a driver datasheet and understand what box-modelling software tells you.

## The acoustic short circuit

When the cone moves forward, it compresses the air in front and rarefies the air behind. The two sides radiate **equal and opposite** pressure waves: the bare driver is a **dipole** (Dan Russell's radiation demo in Further reading shows the field).

At high frequencies the wavelength is short compared with the path from front to back around the cone's edge, so the two waves don't meet in time to cancel much. At low frequencies the wavelength is long, the rear wave easily diffracts round the edge, and it **cancels the front wave**. Air just sloshes from front to back. This is the **acoustic short circuit**, and it's why a bare driver has almost no bass.

```diagram
 bare driver:   front (+)  )  (  rear (-)
                 \_ air sloshes round _/
 on a baffle:   front (+) |  rear (-)
                  longer path, less cancel
```

> [!analogy] Real-world analogy: a paddle in a pond
> Push a small paddle slowly back and forth in a pond and very little water goes anywhere: it just swirls round the paddle's edges from the high side to the low side. Fix the paddle in a wide wall, or put it in a pipe, and the water has to move along instead.
>
> **How it maps:** The paddle is the cone, the water swirling round its edge is the air sloshing from the compressed front to the rarefied back, and the wall or pipe is the baffle or box that stops the short circuit. Slow strokes correspond to low frequencies, where there is plenty of time for the swirl.
>
> **Where it stops:** Water barely compresses, but air does: the air sealed in a box acts as a spring on the cone. And at high frequencies sound has no time to get round the edge at all, which is why a bare driver still has treble.

The cure is to separate front from back:

- A **baffle** (a flat board) lengthens the path, so cancellation starts at a lower frequency.
- An **enclosure** (a box) traps the rear wave completely, or redirects it so it helps.

## Baffle step

Even in a box, the front baffle has a finite size. At high frequencies, where the baffle is large compared with the wavelength, the driver radiates into the **half-space** in front: half a sphere of directions. At low frequencies, where the wavelength is much larger than the baffle, sound diffracts around the cabinet and radiates into the **full space**: the whole sphere.

Engineers often call these "2π" and "4π" radiation, after the solid angle (in steradians) that half a sphere and a whole sphere cover.

For the same cone motion, radiating into half-space gives twice the on-axis sound pressure of full space: the baffle acts like a mirror, adding a coherent "image" source. Doubling pressure is a rise of about 6 dB.

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
