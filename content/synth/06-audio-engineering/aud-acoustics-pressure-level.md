---
id: aud-acoustics-pressure-level
title: Read sound pressure in dB SPL
level: basic
minutes: 3
summary: The air-pressure reference is 20 micropascals RMS.
sourceLesson: aud-acoustics
---

## Sound pressure level: dB SPL

Sound pressure is the changing pressure around the ambient value, measured in pascals (Pa). For a level measurement, we use its RMS value: an average size over a specified time interval. Because the range is so huge, we use decibels relative to a reference of **20 µPa** (20 millionths of a pascal), roughly the quietest 1 kHz tone a young, healthy listener can detect. The sound pressure level is:

```formula
L_p = 20 log_10(p / p_0)
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

The multiplier is 20, not 10, because pressure is a field quantity, like voltage: for a progressive wave in the same medium, sound intensity is proportional to pressure squared, and squaring a ratio doubles its logarithm (module 1 explains why). Worked example for a pressure of 1 Pa:

```formula
L_p = 20 log_10(1 Pa / 0.00002 Pa)
L_p = 20 log_10(50000)
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
    # Compare RMS pressure to 20
    # micropascals.
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

Remember **1 Pa ≈ 94 dB SPL**. Microphone sensitivities are quoted at 1 Pa (the microphone units) and calibrators often produce 94 dB SPL for exactly this reason.

## Key takeaways
- The air-pressure reference is 20 micropascals RMS.
- One pascal RMS is approximately 94 dB SPL.
- Pressure ratios use twenty times the base-ten logarithm.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
