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

```formula
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

The total equivalent absorption area is each surface area multiplied by its frequency-dependent absorption coefficient, summed. Worked through for the 5.0 × 3.6 × 2.4 m studio with bare surfaces averaging an absorption coefficient of 0.10, then with 10 m² of surface swapped for panels with an absorption coefficient of 0.90:

```formula
V = 5.0 × 3.6 × 2.4 = 43.2 m^3
S = 2 × (18 + 12 + 8.64) ≈ 77.3 m^2
A = 77.3 × 0.10 ≈ 7.73 m^2
RT60 = 0.161 × 43.2 / 7.73 ≈ 0.90 s
A_t = 7.73 − 10 × 0.10 + 10 × 0.90
A_t ≈ 15.73 m^2
RT60_t = 0.161 × 43.2 / 15.73 ≈ 0.44 s
where
V: the room's volume, in cubic metres (m³): length × width × height
S: the total surface area of the six faces, in square metres (m²): 2 × (5.0 × 3.6 + 5.0 × 2.4 + 3.6 × 2.4)
A: the bare room's total absorption, in square metres (m²): its area times the average absorption coefficient 0.10
RT60: the bare room's reverberation time, in seconds (s)
A_t: the treated room's absorption: remove 10 m² at 0.10, add 10 m² at 0.90
RT60_t: the treated room's reverberation time, in seconds (s)
0.161: Sabine's constant, in seconds per metre (s/m)
m: metres; m^2 is square metres, m^3 cubic metres
s: seconds
In words: ten square metres of good absorbers roughly doubles the room's absorption, so the reverberation time halves from about 0.9 s to about 0.44 s.
```

The same calculation as a Python script:

```python
import math

Lx, Ly, Lz = 5.0, 3.6, 2.4
V = Lx * Ly * Lz
S = 2 * (Lx*Ly + Lx*Lz + Ly*Lz)

A_bare = S * 0.10          # avg alpha 0.1
rt_bare = 0.161 * V / A_bare
# swap 10 m^2 of alpha 0.1 for 0.9 panels
A_tr = A_bare - 10 * 0.10 + 10 * 0.90
# The model is evaluated for one band.
rt_tr = 0.161 * V / A_tr

print(f"V={V:.1f} m3, S={S:.1f} m2")
print(f"bare:    RT60={rt_bare:.2f} s")
print(f"treated: RT60={rt_tr:.2f} s")
fs = 2000 * math.sqrt(rt_tr / V)
print(f"Schroeder ~{fs:.0f} Hz")
```

```output
V=43.2 m3, S=77.3 m2
bare:    RT60=0.90 s
treated: RT60=0.44 s
Schroeder ~202 Hz
```

Ten square metres of effective absorption halves the reverberation time. Two caveats:

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
