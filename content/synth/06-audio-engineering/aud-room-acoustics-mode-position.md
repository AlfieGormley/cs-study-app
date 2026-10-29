---
id: aud-room-acoustics-mode-position
title: Relate modal frequencies to room position
level: advanced
minutes: 3
summary: Coincident modal frequencies do not alone predict the response at a particular seat.
sourceLesson: aud-room-acoustics
---

## Room dimensions and listener position

### An example room

A small studio of 5.0 × 3.6 × 2.4 m. Each dimension has its own series of axial modes, whole-number multiples of its lowest one (the previous lesson):

| Dimension | First three axial modes |
|---|---|
| Length 5.0 m | 34.3, 68.6, 102.9 Hz |
| Width 3.6 m | 47.6, 95.3, 142.9 Hz |
| Height 2.4 m | 71.5, 142.9, 214.4 Hz |

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
