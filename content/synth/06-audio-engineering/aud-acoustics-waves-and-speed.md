---
id: aud-acoustics-waves-and-speed
title: Pressure waves, speed and wavelength
level: basic
minutes: 5
summary: Sound in air is a longitudinal pressure disturbance; molecules oscillate locally.
sourceLesson: aud-acoustics
---

Everything in this module happens in air. Your synth makes a voltage; a loudspeaker turns it into moving air; a room bounces it about; an ear or a microphone turns it back into something useful. Before looking at any of those devices, you need a working model of what sound in air actually is and how it behaves with distance.

Module 1 covered decibels as ratios and dBFS, and module 5 covered dBu and dBV for signal voltages. This lesson adds the decibel scale for *sound in air*: dB SPL.

## Sound is a pressure wave

A loudspeaker cone moving forward squashes the air in front of it slightly (a **acoustic compression**); moving back, it leaves the air slightly thinner (a **rarefaction**). Each layer of air pushes on the next, so the disturbance travels outward. The air molecules themselves only jiggle back and forth around where they started. What travels is the *pattern* of pressure.

```diagram
 cone   compression   rarefaction
  |  ||||||||    |   |   |   |||||||
  |  ||||||||    |   |   |   |||||||
  ---------> direction of travel
```

Two consequences matter for audio engineering:

- Sound is **longitudinal**: the air moves along the direction of travel, not across it.
- The pressure changes are **tiny**. Atmospheric pressure is about 101,325 Pa. A 120 dB SPL sound has an RMS pressure of 20 Pa; a 60 dB SPL sound has an RMS pressure of 0.02 Pa. These are pressure examples, not hearing-safety thresholds.

## Speed of sound and wavelength

In dry air the speed of sound depends mainly on temperature: warmer air molecules move faster, so they pass the disturbance on faster. For ideal dry air at fixed temperature, static pressure cancels from the sound-speed relation. Humidity also changes the speed, so precise outdoor alignment needs the actual conditions. A standard ideal-gas approximation, good for everyday air temperatures, is:

```formula
c = 331.3 √(1 + T / 273.15)
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
c = 331.3 √(1 + 20 / 273.15)
c = 331.3 √(1.0732)
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

The approximation assumes dry air behaving as an ideal gas. Humidity generally raises the speed; its effect depends on temperature and water-vapour content. The dry-air calculation is an approximation, not a measured outdoor value. The same calculation as a short program:

```python
import math

def c_air(t_c):
    # Dry-air model; return metres/second.
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
λ = (343 m/s) / (1000 Hz)
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

## Key takeaways
- Sound in air is a longitudinal pressure disturbance; molecules oscillate locally.
- Temperature changes sound speed and therefore travel time.
- At a fixed sound speed, doubling frequency halves wavelength.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
