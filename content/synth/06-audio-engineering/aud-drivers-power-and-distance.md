---
id: aud-drivers-power-and-distance
title: Work backwards from required listener level
level: intermediate
minutes: 4
summary: Use a consistent reference, spectrum and far-field measurement direction.
sourceLesson: aud-drivers
---

## Power, distance and efficiency

To predict how loud a speaker will be, start from its sensitivity, add the decibels gained by using more than 1 W, and subtract the decibels lost by listening further away than 1 m. For a fixed signal spectrum in the linear range, use this approximate on-axis free-field, far-field estimate (neglecting air absorption and power compression):

```formula
SPL = S + 10 log_10(P / 1 W)
      − 20 log_10(r / 1 m)
where
SPL: the sound pressure level at the listener, in decibels (dB SPL)
S: the speaker's sensitivity, in dB SPL at 1 W / 1 m; typically 84–90 dB for hi-fi, over 100 dB for PA horns
P: the amplifier power into the speaker's nominal impedance, in watts (W)
r: the listening distance from the speaker, in metres (m); in the actual source’s far field; one metre is a reference distance, not a universal far-field boundary
log_10: the base-10 logarithm
W: watt
m: metre
dB: decibel
In words: every doubling of power adds about 3 dB (10 × log_10 because power is already a power quantity), and every doubling of distance takes away about 6 dB (20 × log_10, the inverse square law for pressure).
```

Each **doubling of power adds only 3 dB**; ten times the power adds 10 dB. For an 87 dB/1 W/1 m speaker at 1 m (so the distance term is zero):

```formula
SPL = 87 + 10 log_10(100 W / 1 W)
SPL = 87 dB + 20 dB = 107 dB SPL
P = 1 W × 10^{(L_t − S)/10}
P = 1 W × 10^{(105 − 87)/10} ≈ 63 W
where
SPL: the level at 1 m, in dB SPL
P: the amplifier power, in watts (W)
L_t: the target level, here 105 dB SPL
S: the sensitivity, here 87 dB at 1 W / 1 m
log_10: the base-10 logarithm
10^{…}: ten to the power of the bracket; it undoes 10 × log_10, turning decibels back into a power ratio
W: watt
dB: decibel
≈: approximately equal to (rounded)
In words: 100 W gives 20 dB more than 1 W; going the other way, reaching 105 dB SPL needs 18 dB more than 1 W, which is about 63 W.
```

The same in Python:

```python
import math

sens = 87  # dB SPL, 1 W / 1 m
for p in (1, 2, 10, 100):
    # Power ratio is relative to one watt.
    spl = sens + 10 * math.log10(p)
    print(f"{p:>3} W: {spl:5.1f} dB @ 1 m")

# power for 105 dB SPL at 1 m:
print(round(10 ** ((105 - sens) / 10), 1))
```

```
  1 W:  87.0 dB @ 1 m
  2 W:  90.0 dB @ 1 m
 10 W:  97.0 dB @ 1 m
100 W: 107.0 dB @ 1 m
63.1
```

Worked example (from Purdue's notes): you want 90 dB SPL at 4 m outdoors from an 86 dB/1 W/1 m speaker. Work backwards: first the distance loss, then the level needed at 1 m, then the power.

```formula
D = 20 log_10(4 m / 1 m) ≈ 12 dB
L_1 = 90 dB + 12 dB = 102 dB SPL
L_1 − S = 102 dB − 86 dB = 16 dB
P = 1 W × 10^{16/10} ≈ 40 W
where
D: the level lost between 1 m and 4 m, in decibels (dB)
L_1: the level needed at 1 m, in dB SPL
S: the speaker's sensitivity, 86 dB SPL at 1 W / 1 m
P: the amplifier power needed, in watts (W)
log_10: the base-10 logarithm
10^{…}: ten to the power of the bracket, turning decibels back into a power ratio
m: metre
W: watt
dB: decibel
SPL: sound pressure level
≈: approximately equal to (rounded)
In words: 4 m costs about 12 dB, so you need 102 dB at 1 m, 16 dB above the 1 W figure, which is about 40 times the power: **40 W**, before any headroom for peaks.
```

Every 3 dB of sensitivity halves the amplifier power needed for the same level. Sensitivity is closely related to **loudspeaker efficiency**, the fraction of electrical power that comes out as sound:

```formula
η = P_ac / P_el
P_ac = 0.01 × 40 W = 0.4 W
where
η: eta, the efficiency, a fraction (or percentage); around 0.01 (1%) for a typical home loudspeaker
P_ac: the acoustic power radiated as sound, in watts (W)
P_el: the electrical power from the amplifier, in watts (W)
W: watt
In words: efficiency is sound power out divided by electrical power in; at 1%, 40 W of amplifier power makes only about 0.4 W of sound.
```

The rest becomes heat, mostly in the voice coil.

## Key takeaways
- Use a consistent reference, spectrum and far-field measurement direction.
- Distance loss can demand much more power than a sensitivity comparison alone suggests.
- Leave appropriate peak margin while respecting driver excursion and thermal limits.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
