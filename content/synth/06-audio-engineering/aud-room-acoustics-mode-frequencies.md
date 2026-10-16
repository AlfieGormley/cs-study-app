---
id: aud-room-acoustics-mode-frequencies
title: Calculate rectangular-room mode frequencies
level: advanced
minutes: 4
summary: Ideal rectangular rigid rooms have axial, tangential and oblique mode families.
sourceLesson: aud-room-acoustics
---

Put the best monitors in the world in an untreated, square, bare-walled room and you'll hear the room as much as the speakers. Below a few hundred hertz, a small room's response at your listening position can swing by 20 dB or more between neighbouring frequencies. Mix there and you'll correct for problems that only exist in your room, and the mix will sound wrong everywhere else.

This lesson is about understanding what a room does, then placing monitors and treatment so you can trust what you hear.

## Room modes

Between two parallel walls, a sound wave reflects back and forth. At frequencies where a whole number of half-wavelengths fits exactly between the walls, the reflections reinforce each other into a **standing wave**: a **room mode** (or resonance).

To find those frequencies, start from the fact that one half-wavelength, two half-wavelengths, three and so on must fit the gap exactly, then use the link between wavelength, frequency and the speed of sound:

```formula
L = nλ / 2
λ = c / f_n
f_n = nc / (2L)
where
f_n: the frequency of the nth mode between this pair of walls, in hertz (Hz)
n: the mode number, a whole number 1, 2, 3 …; mode 1 is the lowest (fundamental), mode 2 is twice its frequency, and so on
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
L: the distance between the two parallel walls, in metres (m)
λ: lambda, the wavelength of the sound, in metres (m): the distance one cycle of the wave covers in air
In words: the lowest mode is the frequency whose half-wavelength exactly spans the gap between the walls, and every whole-number multiple of it is a mode too. The bigger the room, the lower the modes.
```

For two walls 5.0 m apart, the first mode is 343 ÷ (2 × 5.0) = 34.3 Hz, the second 68.6 Hz and the third 102.9 Hz. The formula assumes rigid, parallel, flat walls; real walls flex and absorb a little, which damps and slightly shifts the modes.

Those are **axial modes**: between one pair of surfaces. They usually carry the most energy and have the greatest influence on the low-frequency response. **Tangential modes** involve two pairs of surfaces and **oblique modes** all three. For a rectangular (shoebox) room, one formula covers all three kinds (exclude the all-zero mode-number combination, which is static pressure rather than an oscillating acoustic mode):

```formula
f = (c / 2) √((n_x / L_x)^2
    + (n_y / L_y)^2 + (n_z / L_z)^2)
where
f: the frequency of the mode, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s)
√: the square root of everything inside the brackets that follow it
n_x: the mode number along the length: 0, 1, 2 … (0 means the mode doesn't involve that pair of walls)
n_y: the mode number along the width: 0, 1, 2 …
n_z: the mode number along the height: 0, 1, 2 …
L_x: the room's length, in metres (m)
L_y: the room's width, in metres (m)
L_z: the room's height, in metres (m)
In words: each mode is labelled by three whole numbers saying how many half-wavelengths it has along each dimension. One non-zero number gives an axial mode, two a tangential mode, three an oblique mode.
```

When only one mode number is non-zero this reduces to the axial formula above. A tangential example, the (1, 1, 0) mode of a room with a 5.0 × 3.6 m floor plan:

```formula
f = (343 / 2) √((1 / 5.0)^2
    + (1 / 3.6)^2)
f ≈ 171.5 √(0.040 + 0.077)
f ≈ 171.5 × 0.342 ≈ 58.7 Hz
where
f: the frequency of the (1, 1, 0) tangential mode, in hertz (Hz)
√: the square root of the bracket that follows
≈: approximately equal to (values rounded)
Hz: hertz, cycles per second
In words: one half-wavelength along the length and one across the width combine into a mode at about 58.7 Hz, higher than either of the axial modes it combines (34.3 Hz and 47.6 Hz).
```

Like the axial formula, it assumes rigid walls and a perfectly rectangular room.

## Key takeaways
- Ideal rectangular rigid rooms have axial, tangential and oblique mode families.
- Mode frequency depends on room dimensions and mode numbers.
- Wall flexibility and absorption modify the ideal result.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
