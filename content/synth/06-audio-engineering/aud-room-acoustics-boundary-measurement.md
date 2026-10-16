---
id: aud-room-acoustics-boundary-measurement
title: Diagnose boundary notches and measure the room
level: advanced
minutes: 4
summary: A reflected path can cancel direct sound at particular frequencies.
sourceLesson: aud-room-acoustics
---

## Boundary interference

### Wall distance and SBIR

Sound radiates backwards from a monitor at low frequencies (it's omnidirectional there; the driver and enclosure units). That rear sound reflects off the front wall and returns. Where the reflected travel delays it by half a period, which happens when the distance to the wall is a **quarter wavelength**, it cancels the direct sound: **speaker boundary interference response (SBIR)**.

The reflected sound travels to the wall and back, an extra distance of twice the speaker-to-wall gap. The first cancellation happens when that extra distance is half a wavelength, so the wave comes back upside down:

```formula
2d = λ / 2
λ = c / f_notch
f_notch ≈ c / (4d)
f_notch ≈ 343 / (4 × 0.5) ≈ 172 Hz
where
f_notch: the frequency of the first (lowest) cancellation notch, in hertz (Hz)
d: the distance from the speaker's acoustic source to the wall behind it, in metres (m); here 0.5 m
λ: lambda, the wavelength, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s)
≈: approximately equal to; this simple model only counts the straight-back-and-forth path
Hz: hertz, cycles per second
In words: the notch sits at the frequency whose quarter wavelength equals the speaker-to-wall distance, so moving the speaker closer to the wall pushes the notch up in frequency.
```

This assumes the wall is rigid and the reflection travels straight back (the wall-perpendicular path). Real notches are shallower than a perfect cancellation and are partly filled by other paths. The same calculation for other distances:

| Speaker to front wall | First notch |
|---|---|
| 0.3 m | ≈ 286 Hz |
| 0.5 m | ≈ 172 Hz |
| 0.6 m | ≈ 143 Hz |
| 1.0 m | ≈ 86 Hz |

Genelec’s guide describes deep cancellation notches and advises against fixing them by boosting EQ. EQ scales both direct and reflected sound: a perfect null remains zero, while a finite dip can be raised locally only at the cost of headroom and potentially worse sound elsewhere. EQ does not remove the reflection or its geometry. Their remedies:

- **Flush-mount** the monitors in a hard wall, which removes the rear reflection.
- **Place them close to the wall**: typically with the front of the monitor less than 60 cm from the wall, so the notch moves up to frequencies where the speaker radiates less backwards, while leaving at least 5 cm clearance for a rear port.

The same cancellation happens with side walls, the floor and the desk at different distances, so varying those distances spreads the notches rather than stacking them.

## Measuring a room with REW

You can't fix what you can't measure, and ears are bad at judging bass in a room. **Room EQ Wizard (REW)** is free room-acoustics software for Windows, macOS and Linux. With a **calibrated measurement microphone** (for example a USB mic supplied with a calibration file), it:

- Plays a **swept sine** through your monitors and records it at the listening position.
- Computes the **impulse response**, and from it the **frequency response**, **waterfall plot** (how each frequency decays over time, which shows ringing modes clearly) and **decay / RT60** figures.
- Helps identify **room modes** and can calculate EQ filters.

A practical workflow:

1. Measure each monitor separately at the listening position, at a moderate level (the hearing units: protect your ears).
2. Look for big peaks and deep notches below about 300 Hz, and long decay in the waterfall.
3. Move the listening position and speakers first; that changes modes and SBIR far more than EQ can.
4. Add bass traps and first-reflection absorption, and re-measure.
5. Only then use EQ, mainly to **cut peaks**. Don't try to fill deep notches with boost: they're cancellations, and boosting them wastes amplifier power and driver excursion.

## Key takeaways
- A reflected path can cancel direct sound at particular frequencies.
- Placement and effective treatment change the reflection geometry; EQ does not remove it.
- Measure, change one cause and remeasure before applying final peak cuts.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
- [Acoustic treatment and boundary interference — Genelec](https://store.genelec.com/web/site/improving-room-acoustics)
