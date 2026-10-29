---
id: aud-acoustics-waves-and-speed
title: Pressure waves, speed and wavelength
level: basic
minutes: 4
summary: Sound in air is a longitudinal pressure disturbance; molecules oscillate locally.
sourceLesson: aud-acoustics
---

Everything in this module happens in air. Your synth makes a voltage; a loudspeaker turns it into moving air; a room bounces it about; an ear or a microphone turns it back into something useful. Before looking at any of those devices, you need a working model of what sound in air actually is and how it behaves with distance.

Module 1 covered decibels as ratios and dBFS, and module 5 covered dBu and dBV for signal voltages. The next lesson adds the decibel scale for *sound in air*: dB SPL.

## Sound is a pressure wave

A loudspeaker cone moving forward squashes the air in front of it slightly (an **acoustic compression**); moving back, it leaves the air slightly thinner (a **rarefaction**). Each layer of air pushes on the next, so the disturbance travels outward. The air molecules themselves only jiggle back and forth around where they started. What travels is the *pattern* of pressure.

```diagram
 cone   compression   rarefaction
  |  ||||||||    |   |   |   |||||||
  |  ||||||||    |   |   |   |||||||
  ---------> direction of travel
```

Two consequences matter for audio engineering:

- Sound is **longitudinal**: the air moves along the direction of travel, not across it.
- The pressure changes are **tiny**. Atmospheric pressure is about 101,325 Pa. A 120 dB SPL sound has an RMS pressure of 20 Pa; a 60 dB SPL sound has an RMS pressure of 0.02 Pa. These are pressure examples, not hearing-safety thresholds.

> [!analogy] Real-world analogy: a shove passed along a packed line of people
> Picture people standing shoulder to shoulder in a tight line. Someone at the back is nudged forward; they bump the person in front, who bumps the next, and the bump runs to the front. Nobody walks to the front of the line; each person sways forward and back.
>
> **How it maps:** The people are layers of air. A bunched-up stretch of the line is a compression, a gap is a rarefaction, and the bump moving along is the sound wave. Each person sways along the line's direction, which is what longitudinal means.
>
> **Where it stops:** Air is not a single file: the disturbance spreads out in three dimensions. Its speed is set by the air's properties, mainly temperature, not by how quickly people react, and real air molecules also move randomly at high speed all the time.

## Speed of sound

The speed of sound in air is set by the air itself, not by how loud the sound is or its pitch. In dry air it depends mainly on temperature: warmer air passes the disturbance on faster. For ideal dry air at a fixed temperature, static pressure cancels out of the sound-speed relation, so weather fronts matter much less than temperature. Humidity raises the speed a little, so precise outdoor alignment needs the actual conditions.

The working figure is **343 m/s at 20 °C**, about 1 metre every 2.9 ms. Near room temperature it changes by roughly 0.6 m/s for each degree; at 0 °C it is about 331 m/s. That speed turns up everywhere: speaker delay times, room modes, crossover alignment.

```formula reference
c ≈ 331.3 √(1 + T / 273.15)
where
c: the speed of sound in dry air, in metres per second (m/s)
T: the air temperature, in degrees Celsius (°C); everyday values are about 0–35 °C
331.3: the speed of sound in dry air at 0 °C, in m/s
273.15: the number you add to a Celsius temperature to get kelvin (absolute temperature), so 1 + T / 273.15 is the absolute temperature divided by that of 0 °C
√: square root: the number that, multiplied by itself, gives what is inside the brackets
≈: approximately equal to; the relation treats dry air as an ideal gas
In words: Sound speed in dry air rises with the square root of absolute temperature; near room temperature that is about 0.6 metres per second faster for each degree warmer, giving about 343 metres per second at 20 °C.
```

## Wavelength

**Wavelength** is how far the wave travels during one cycle. In one second sound covers about 343 m and completes as many cycles as its frequency, so each cycle covers the speed divided by the frequency. This inverse relationship is the key to the rest of the module:

```formula essential
λ = c / f
where
λ: lambda, the wavelength: the distance the wave travels during one cycle, in metres (m)
c: the speed of sound, about 343 metres per second (m/s) at 20 °C
f: the frequency of the sound, in hertz (Hz)
Hz: hertz, the unit of frequency: one cycle per second
In words: the wavelength is the speed of sound divided by the frequency, so doubling the frequency halves the wavelength.
```

| Frequency | Wavelength (at 343 m/s) |
|---|---|
| 20 Hz | 17.15 m |
| 100 Hz | 3.43 m |
| 1 kHz | 34.3 cm |
| 10 kHz | 3.43 cm |
| 20 kHz | 1.7 cm |

Audible wavelengths span a factor of 1,000, from longer than a house to shorter than your thumb. That is why one room, one speaker cabinet or one absorber can behave completely differently at the bottom and the top of the audio range. Relative size strongly affects diffraction and scattering; reflection and absorption also depend on material impedance, construction, mounting and incidence angle.

The same relationship applies in other media with that medium's own speed: sound in water travels about four times faster than in air, so a given frequency has a wavelength about four times longer. Frequency is set by the source; when the speed changes, the wavelength changes with it.

## Key takeaways
- Sound in air is a longitudinal pressure disturbance; molecules oscillate locally.
- Temperature changes sound speed and therefore travel time: about 343 m/s at 20 °C, about 0.6 m/s per degree.
- At a fixed sound speed, doubling frequency halves wavelength; audible wavelengths run from about 17 m to 1.7 cm.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
