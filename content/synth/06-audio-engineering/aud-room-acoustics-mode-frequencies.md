---
id: aud-room-acoustics-mode-frequencies
title: Predict rectangular-room mode frequencies
level: advanced
minutes: 4
summary: Ideal rectangular rigid rooms have axial, tangential and oblique mode families.
sourceLesson: aud-room-acoustics
---

Put the best monitors in the world in an untreated, square, bare-walled room and you'll hear the room as much as the speakers. Below a few hundred hertz, a small room's response at your listening position can swing by 20 dB or more between neighbouring frequencies. Mix there and you'll correct for problems that only exist in your room, and the mix will sound wrong everywhere else.

This lesson is about understanding what a room does, then placing monitors and treatment so you can trust what you hear.

## Room modes

Between two parallel walls, a sound wave reflects back and forth. At frequencies where a whole number of half-wavelengths fits exactly between the walls, the reflections reinforce each other into a **standing wave**: a **room mode** (or resonance).

The rule that one half-wavelength, two half-wavelengths, three and so on must fit the gap exactly, combined with the link between wavelength and frequency, gives the mode frequencies between one pair of walls:

```formula essential
f_n = nc / (2L)
where
f_n: the frequency of the nth mode between this pair of walls, in hertz (Hz)
n: the mode number, a whole number 1, 2, 3 …; mode 1 is the lowest (fundamental), mode 2 is twice its frequency, and so on
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
L: the distance between the two parallel walls, in metres (m)
In words: the lowest mode is the frequency whose half-wavelength exactly spans the gap between the walls, and every whole-number multiple of it is a mode too. The bigger the room, the lower the modes.
```

For two walls 5.0 m apart, the first mode is about 34 Hz, the second about 69 Hz and the third about 103 Hz: whole-number multiples of the first, not equal steps from an arbitrary start. Halve the spacing and every mode doubles in frequency. The relationship assumes rigid, parallel, flat walls; real walls flex and absorb a little, which damps and slightly shifts the modes.

> [!analogy] Real-world analogy: a skipping rope
> Two people turning a long skipping rope can make it swing in one big loop, or, turning faster, in two loops with a still point in the middle, or three. In between those rhythms the rope just flails without settling into a steady shape.
>
> **How it maps:** The rope's length is the distance between the walls. Each steady shape is a mode: one loop is the first mode (half a wavelength across the gap), two loops the second, and so on, at whole-number multiples of the slowest rhythm. The still points are the nodes.
>
> **Where it stops:** The rope is held still at its ends, whereas sound pressure is at its *maximum* at a rigid wall. And a room is three-dimensional, so modes also form across the width, the height and diagonally, all at once.

Those are **axial modes**: between one pair of surfaces. They usually carry the most energy and have the greatest influence on the low-frequency response. **Tangential modes** involve two pairs of surfaces and **oblique modes** all three. For a rectangular (shoebox) room, one relationship covers all three kinds; exclude the all-zero combination, which is static pressure rather than an oscillating acoustic mode:

```formula reference
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
In words: Each rectangular-room mode is labelled by three whole numbers counting half-wavelengths along the length, width and height; one non-zero number gives an axial mode, two a tangential mode and three an oblique mode.
```

A tangential mode always sits higher than the axial modes it combines. For a 5.0 × 3.6 m floor plan, the axial modes along the length and width are about 34 Hz and 48 Hz, and the tangential mode combining them is about 59 Hz. Like the axial relationship, this assumes rigid walls and a perfectly rectangular room.

## Key takeaways
- Ideal rectangular rigid rooms have axial, tangential and oblique mode families.
- Mode frequency depends on room dimensions and mode numbers.
- Wall flexibility and absorption modify the ideal result.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
