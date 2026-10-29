---
id: aud-acoustics-boundaries-and-fields
title: Relating wavelength to boundaries and fields
level: basic
minutes: 4
summary: Size relative to wavelength affects diffraction and acoustic shadows.
sourceLesson: aud-acoustics
---

## Reflection, absorption and diffraction

At a boundary, sound can be reflected, transmitted or absorbed; diffraction describes spreading around edges and openings. Wavelength, impedance and construction all matter.

**Sound reflection.** A hard, large, flat surface (a wall, a desk, a window) reflects sound like a mirror reflects light: angle in equals angle out. This only works well when the surface is large compared with the wavelength. A stiff 30 cm panel can give a directional reflection at 10 kHz (wavelength 3.4 cm). At 100 Hz (wavelength 3.4 m), diffraction around it is important; its actual reflection and transmission still depend on material and mounting.

**Sound absorption.** Porous materials (mineral wool, thick fabric) turn some of the sound's energy into heat. Each material has an **absorption coefficient**: the fraction of the arriving energy that is not returned as reflected sound, in the room-acoustics convention (it may include energy transmitted through the surface). It has no unit and runs from 0, a perfect reflector, to 1, where nothing comes back, as from an open window. A panel that reflects 30 % of the arriving energy has an absorption coefficient of 0.7.

The coefficient varies with frequency, so it is quoted per octave band. Thin foam absorbs high frequencies well and does almost nothing to bass, because bass wavelengths are far longer than the foam is thick.

**Diffraction.** Waves bend around obstacles and spread out through openings. When an obstacle is small compared with the wavelength, sound diffracts around it with hardly a shadow. When it's large, it casts an acoustic shadow. This is why you can hear the bass, but not the cymbals, from a band round the corner; why your head shadows high frequencies but not low ones (the hearing units); and why a loudspeaker radiates almost equally in all directions at low frequencies but beams forward at high frequencies (the loudspeaker-driver units).

| Size vs wavelength | Behaviour |
|---|---|
| Object much smaller | Sound diffracts round it |
| Comparable | Partial, frequency-dependent |
| Object much larger | Reflection and shadowing |

> [!analogy] Real-world analogy: sea waves at a harbour
> Ocean swell meets a thin mooring post and simply closes up behind it; the water just behind the post is as choppy as anywhere else. The same swell meeting a long harbour wall leaves a calm patch of water in its lee.
>
> **How it maps:** The post is an object much smaller than the wavelength, so the wave diffracts round it with almost no shadow, like bass passing a person or a speaker stand. The harbour wall is much larger than the wavelength, so it reflects and shadows, like a building blocking cymbals.
>
> **Where it stops:** Sea waves move along a surface and are easy to see; sound spreads in three dimensions as pressure. Whether a real surface reflects, transmits or absorbs sound also depends on its material and mounting, which the size comparison alone does not tell you.

## Near field and far field

Very close to a source, the sound field is complicated: different parts of the source (the cone, the edges of the cabinet, several drivers) are at noticeably different distances from you, and their contributions interfere. Level can change sharply as you move a few centimetres, and it doesn't follow the inverse square law.

Further away, in the **far field**, the source behaves like a point: level falls 6 dB per doubling, and the balance between drivers settles down. The distance needed depends on source geometry, frequency and the measurement criterion. Several source dimensions alone is not a universal far-field test for a large array; follow the manufacturer's measurement method and verify that distance-scaled responses converge. Datasheet figures are quoted "at 1 m", but large speakers are often measured further away and the result scaled back to 1 m with the inverse square law.

> [!tip] "Near-field monitor" means something else
> Studio "near-field monitors" are small speakers listened to from about 1–2 m, so that you hear more direct sound than room reflections. They aren't about the acoustic near field of the speaker itself. The room-acoustics units cover them.

## Key takeaways
- Size relative to wavelength affects diffraction and acoustic shadows.
- Absorption also depends on material, mounting and incidence angle.
- A reverberant room and an acoustic near field do not follow a simple distance law.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
