---
id: aud-acoustics-distance-loss
title: Predict free-field distance loss
level: basic
minutes: 4
summary: Use the same direction and a source’s free-field far field.
sourceLesson: aud-acoustics
---

## The inverse square law

A small source in open space (a **free field**, with no reflections) spreads its power over the surface of a growing sphere. A sphere's area grows with the square of its radius, so at twice the distance the same acoustic power is shared over four times the area. The **sound intensity** (power per square metre) therefore falls to a quarter, and because intensity is proportional to pressure squared, the RMS pressure halves.

```formula reference
I = P_ac / (4πr^2)
p ∝ 1 / r
where
I: the sound intensity: the acoustic power passing through each square metre, in watts per square metre (W/m²)
P_ac: the acoustic power the source radiates, in watts (W); this is sound power, not the amplifier's electrical power
π: pi, the ratio of a circle's circumference to its diameter, about 3.14159
r: the distance from the source, in metres (m)
p: the RMS sound pressure at distance r, in pascals (Pa)
∝: "is proportional to": when one side is multiplied by some factor, the other is multiplied by the same factor
In words: The same acoustic power is spread over a sphere whose area grows with the square of the distance, so intensity falls with distance squared and pressure falls in proportion to distance.
```

> [!analogy] Real-world analogy: a spray can
> Hold a spray can close to a wall and you get a small, dense patch. Step back to twice the distance and the same spray covers a patch twice as wide and twice as tall: four times the area, so each square centimetre gets a quarter of the paint.
>
> **How it maps:** The paint per second is the source's acoustic power, the patch is the sphere the sound spreads over, and paint per square centimetre is intensity. Doubling distance quarters intensity in both cases.
>
> **Where it stops:** Paint droplets fly in straight lines and stick. Sound reflects off walls and bends round objects, so indoors the reflected sound tops the level up and the simple quartering no longer holds.

This is the **inverse square law**. In decibels it becomes a rule about *ratios* of distance, which is what makes it easy to use:

```formula reference
L_2 = L_1 − 20 log_10(r_2 / r_1)
where
L_1: the measured level at distance r_1, in dB SPL
L_2: the predicted level at distance r_2, in dB SPL
r_1: the distance where you know the level, in metres (m)
r_2: the distance you want the level at, in metres (m)
log_10: the base-10 logarithm
In words: In decibels the loss depends only on how many times further away you are, not on the extra metres: about 6 dB for every doubling of distance and 20 dB for every tenfold increase.
```

Two landmarks cover almost every estimate:

- Each **doubling of distance** costs about **6 dB**: 1 m to 2 m loses the same as 10 m to 20 m.
- Each **tenfold increase** in distance costs **20 dB**.

So a speaker giving 100 dB SPL at 1 m gives about 94 dB at 2 m, 88 dB at 4 m and 80 dB at 10 m. Counting doublings is usually all you need. The flip side matters for noise problems: walking a few metres further from a source that is already far away barely changes the level, because a few metres is a small *ratio*.

These figures assume the same direction from the source, measurement in its far field (a later lesson explains), negligible air absorption and no reflections. Outdoors, ground reflection, wind and temperature gradients change real results, so treat predictions as first estimates.

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
