---
id: aud-room-acoustics-reverberation
title: Estimate decay with Sabine’s equation
level: advanced
minutes: 5
summary: Reverberation time describes a sixty-decibel decay.
sourceLesson: aud-room-acoustics
---

## Reverberation and RT60

After a sound stops, its reflections take time to die away. **RT60** is the time for the sound level to fall by **60 dB**. Wallace Sabine's empirical equation (from experiments at Harvard around 1900) relates it to the room's volume and absorption. Use it to estimate how live a room will sound, and how much treatment you'd need to change that:

```formula reference
RT60 = 0.161V / A
A = Σ (S_i α_i)
where
RT60: the reverberation time, in seconds (s): how long the sound takes to fall by 60 decibels (dB) after the source stops
0.161: Sabine's constant for metric units, in seconds per metre (s/m); it comes from 24 × ln(10) ÷ 343 ≈ 0.161, where 343 m/s is the speed of sound
V: the room's volume, in cubic metres (m³)
A: the room's total absorption, in square metres (m²), also called metric sabins: the area of open window that would absorb the same amount
Σ: sigma, "add up the following for every surface"
i: a counter that runs over the room's surfaces (walls, floor, ceiling, panels)
S_i: the area of surface i, in square metres (m²)
α_i: alpha, the absorption coefficient of surface i: the effective fraction of incident energy not returned by that surface at the frequency considered, from 0 (perfect reflector) to 1 (perfect absorber)
In words: reverberation time grows with the room's volume and shrinks with how much absorbing surface it contains. Double the absorption and you halve RT60.
```

The total equivalent absorption area is each surface area multiplied by its frequency-dependent absorption coefficient, summed. The relationship has two levers, and the second is usually the only practical one:

- **Volume.** A bigger room, with the same surfaces, takes longer to die away.
- **Absorption.** Doubling the total absorption halves the reverberation time. Because hard surfaces absorb so little, a modest area of effective absorbers can dominate the total.

For example, a 5.0 × 3.6 × 2.4 m studio (43.2 m³, about 77 m² of surface) with bare surfaces averaging an absorption coefficient of 0.10 has about 7.7 m² of absorption and an RT60 of about 0.9 s. Swap 10 m² of that surface for panels with a coefficient of 0.90 and the absorption roughly doubles, to about 15.7 m²: the RT60 falls to about 0.44 s. Ten square metres of panels, about an eighth of the surface, halved the decay time.

> [!analogy] Real-world analogy: a bath and its plughole
> Pull the plug on a full bath and it drains at a rate set by the size of the plughole. A bigger bath takes longer to empty through the same plughole; a second plughole empties it twice as fast.
>
> **How it maps:** The water is the sound energy left in the room after the source stops. The bath's size is the room's volume, and the plugholes are its absorption: each absorbing surface is another hole letting energy out. Double the absorption and the room "drains" in half the time.
>
> **Where it stops:** A bath empties at a roughly steady rate, whereas sound energy dies away by the same *fraction* in each moment, so its level falls steadily in decibels. And a room's plugholes change size with frequency: panels that drain the treble quickly may barely touch the bass.

Two caveats:

- **Absorption coefficients depend on frequency.** A treatment that works at 2 kHz may do almost nothing at 100 Hz, so RT60 is quoted per octave band, and a room can be dead in the treble while still booming in the bass.
- **Sabine assumes a fairly live room with diffuse sound.** At higher broadly distributed absorption a diffuse-field Eyring model can improve the estimate; neither model is guaranteed for a strongly non-diffuse room, and in small rooms below the Schroeder frequency "reverberation time" is a rough description at best.

Control rooms are typically much drier than living rooms; recommended targets vary by standard and room size, so treat any single number as a guide.

## Key takeaways
- Reverberation time describes a sixty-decibel decay.
- Sabine’s model uses room volume and equivalent absorption area.
- The diffuse-field and absorption assumptions limit its use, especially in small rooms.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
