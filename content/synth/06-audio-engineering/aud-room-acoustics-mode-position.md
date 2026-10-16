---
id: aud-room-acoustics-mode-position
title: Relate modal frequencies to room position
level: advanced
minutes: 3
summary: Coincident modal frequencies do not alone predict the response at a particular seat.
sourceLesson: aud-room-acoustics
---

## Room dimensions and listener position

### Worked example

A small studio of 5.0 × 3.6 × 2.4 m. Using the axial formula for each dimension:

```formula
f_1 = c / (2L)
f_1 = 1 × 343 / (2 × 5.0) = 34.3 Hz
f_1 = 1 × 343 / (2 × 3.6) ≈ 47.6 Hz
f_1 = 1 × 343 / (2 × 2.4) ≈ 71.5 Hz
where
f_1: the first (lowest) axial mode along one dimension, in hertz (Hz)
c: the speed of sound, 343 metres per second (m/s)
L: the dimension being tested: 5.0 m length, 3.6 m width, 2.4 m height
Hz: hertz, cycles per second
In words: each dimension has its own lowest mode; the longest dimension gives the lowest one. Multiply each by 2, 3 … for the higher modes.
```

The same calculation in Python, for the first three modes of each dimension:

```python
c = 343
dims = {"length": 5.0, "width": 3.6,
        "height": 2.4}
for name, L in dims.items():
    # Each dimension has its own harmonics.
    modes = [round(n * c / (2 * L), 1)
             for n in (1, 2, 3)]
    print(f"{name:<6} {L} m: {modes}")
```

```output
length 5.0 m: [34.3, 68.6, 102.9]
width  3.6 m: [47.6, 95.3, 142.9]
height 2.4 m: [71.5, 142.9, 214.4]
```

Notice that 3.6 ÷ 2.4 = 1.5, so the width's third mode and the height's second land on the **same frequency, 142.9 Hz**. Coincident modal frequencies can produce strong response peaks, depending on how the sources excite them, the listener position and damping. Rooms whose dimensions are simple multiples of each other (a cube has particularly extensive degeneracy) bunch their modes; unrelated dimensions spread them out more evenly.

What a mode does at your seat depends on **where you sit**:

- For ideal rigid rectangular boundaries, each axial mode has pressure antinodes at its corresponding pair of walls. A general mode may still have nodes along other coordinates on a wall; corners are pressure antinodes of all these ideal modes.
- The first axial mode has a **pressure null** halfway between its walls. At the length midpoint, that ideal mode contributes no pressure; moving away can increase its contribution. The total response also contains direct sound and other modes, so it is not necessarily silent or boomy.
- So bass response varies dramatically with position. This is why many guides suggest avoiding the exact centre of the room for the listening position (Genelec suggests sitting in the front part of the room for music work, and at least 1 m from walls).

## Key takeaways
- Coincident modal frequencies do not alone predict the response at a particular seat.
- Source excitation, damping and listener position all matter.
- Avoid treating a node of one mode as silence in the total sound field.

## Further reading
- [Monitor placement — Genelec](https://www.genelec.com/monitor-placement)
- [Driving room modes — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Measured reverberation and Sabine’s equation — Dan Russell](https://www.acs.psu.edu/drussell/demos/rt60/rt60.html)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
