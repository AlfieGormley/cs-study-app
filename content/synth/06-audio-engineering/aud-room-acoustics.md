---
id: aud-room-acoustics
title: Room acoustics and monitoring
level: advanced
minutes: 19
summary: Room modes and the c/2L axial-mode formula with worked examples, reverberation and RT60 with Sabine's equation, absorption vs diffusion, bass traps, early reflections and the mirror trick, near-field monitor placement (equilateral triangle, wall distance, SBIR), and measuring a room with REW.
---

Put the best monitors in the world in an untreated, square, bare-walled room and you'll hear the room as much as the speakers. Below a few hundred hertz, a small room's response at your listening position can swing by 20 dB or more between neighbouring frequencies. Mix there and you'll correct for problems that only exist in your room, and the mix will sound wrong everywhere else.

This lesson is about understanding what a room does, then placing monitors and treatment so you can trust what you hear.

## Room modes

Between two parallel walls, a sound wave reflects back and forth. At frequencies where a whole number of half-wavelengths fits exactly between the walls, the reflections reinforce each other into a **standing wave**: a **room mode** (or resonance).

```
f(n) = n * c / (2 * L)     n = 1, 2, 3...
```

Those are **axial modes**: between one pair of surfaces. They usually carry the most energy and have the greatest influence on the low-frequency response. **Tangential** modes involve two pairs of surfaces and **oblique** modes all three; the general formula for a rectangular room is:

```
f = (c/2) * sqrt((nx/Lx)^2
                 + (ny/Ly)^2
                 + (nz/Lz)^2)
```

### Worked example

A small studio of 5.0 × 3.6 × 2.4 m:

```python
c = 343
dims = {"length": 5.0, "width": 3.6,
        "height": 2.4}
for name, L in dims.items():
    modes = [round(n * c / (2 * L), 1)
             for n in (1, 2, 3)]
    print(f"{name:<6} {L} m: {modes}")
```

```
length 5.0 m: [34.3, 68.6, 102.9]
width  3.6 m: [47.6, 95.3, 142.9]
height 2.4 m: [71.5, 142.9, 214.4]
```

Notice that 3.6 / 2.4 = 1.5, so the width's third mode and the height's second land on the **same frequency, 142.9 Hz**. Coincident modal frequencies can produce strong response peaks, depending on how the sources excite them, the listener position and damping. Rooms whose dimensions are simple multiples of each other (a cube is the worst) bunch their modes; unrelated dimensions spread them out more evenly.

What a mode does at your seat depends on **where you sit**:

- For ideal rigid rectangular boundaries, each axial mode has pressure antinodes at its corresponding pair of walls. A general mode may still have nodes along other coordinates on a wall; corners are pressure antinodes of all these ideal modes.
- The first axial mode has a pressure **null** halfway between its walls. At the length midpoint, that ideal mode contributes no pressure; moving away can increase its contribution. The total response also contains direct sound and other modes, so it is not necessarily silent or boomy.
- So bass response varies dramatically with position. This is why many guides suggest avoiding the exact centre of the room for the listening position (Genelec suggests sitting in the front part of the room for music work, and at least 1 m from walls).

### The Schroeder frequency

At low frequencies, modes are few and far apart, and the room behaves like a set of resonances. Higher up, modes overlap so densely that the room behaves statistically, as reverberation. The crossover between the two is often estimated by the **Schroeder frequency**:

```
f_S ≈ 2000 * sqrt(RT60 / V)   (V in m^3)
```

Below it, think **modes** (fix with placement and bass traps). Above it, think **reflections and reverberation** (fix with absorption and diffusion).

## Reverberation and RT60

After a sound stops, its reflections take time to die away. **RT60** is the time for the sound level to fall by **60 dB**. Wallace Sabine's empirical equation (from experiments at Harvard around 1900) relates it to the room's volume and absorption:

```
RT60 = 0.161 * V / A
A = sum(S_i * alpha_i)   (sabins, m^2)
```

- **V** is the volume in m³.
- **A** is the total absorption: each surface's area times its **absorption coefficient** α (0 = perfect reflector, 1 = perfect absorber), summed.

```python
import math

Lx, Ly, Lz = 5.0, 3.6, 2.4
V = Lx * Ly * Lz
S = 2 * (Lx*Ly + Lx*Lz + Ly*Lz)

A_bare = S * 0.10          # avg alpha 0.1
rt_bare = 0.161 * V / A_bare
# swap 10 m^2 of alpha 0.1 for 0.9 panels
A_tr = A_bare - 10 * 0.10 + 10 * 0.90
rt_tr = 0.161 * V / A_tr

print(f"V={V:.1f} m3, S={S:.1f} m2")
print(f"bare:    RT60={rt_bare:.2f} s")
print(f"treated: RT60={rt_tr:.2f} s")
fs = 2000 * math.sqrt(rt_tr / V)
print(f"Schroeder ~{fs:.0f} Hz")
```

```
V=43.2 m3, S=77.3 m2
bare:    RT60=0.90 s
treated: RT60=0.44 s
Schroeder ~202 Hz
```

Ten square metres of effective absorption halves the reverberation time. Two caveats:

- **Absorption coefficients depend on frequency.** A treatment that works at 2 kHz may do almost nothing at 100 Hz, so RT60 is quoted per octave band, and a room can be dead in the treble while still booming in the bass.
- **Sabine assumes a fairly live room with diffuse sound.** In very absorbent rooms it overestimates RT60 (the Eyring equation is more accurate there), and in small rooms below the Schroeder frequency "reverberation time" is a rough description at best.

Control rooms are typically much drier than living rooms; recommended targets vary by standard and room size, so treat any single number as a guide.

## Absorption vs diffusion

- **Absorbers** convert sound energy to heat. **Porous absorbers** (mineral wool, fibreglass, thick acoustic foam) work by friction as air moves through them. They're most effective where the air particle velocity is high, which is about a **quarter wavelength from a hard wall**. A thin porous panel against a rigid wall generally absorbs low frequencies poorly. The quarter-wave distance for 10 cm is about 850 Hz, but this is not a cutoff or a prediction of measured absorption: material flow resistance, thickness, mounting and incidence matter. An air gap can improve lower-frequency absorption.
- **Diffusers** scatter sound in many directions without removing much energy. They break up strong specular reflections and flutter echo (rapid repeats between parallel hard walls) while keeping the room feeling live. They need to be large compared with the wavelengths they diffuse, so they work mainly in the mids and highs, and need some distance from the listener.

A good control room usually combines both: absorption where early reflections hit, diffusion or a mix at the back, and bass trapping in the corners.

### Bass traps

Bass wavelengths are metres long, so thin porous panels mounted against a rigid wall generally provide little bass absorption. Thin resonant panel systems are a different mechanism. **Bass traps** are:

- **Thick porous absorbers** (often 10–20 cm or more), commonly placed across **corners**. Straddling a corner leaves a large air gap behind the panel, which extends its effect to lower frequencies.
- **Pressure-based (membrane or Helmholtz) absorbers** tuned to specific low frequencies, which work by resonance and are most effective at pressure maxima such as walls and corners.

Corners are useful because modes from all three dimensions have pressure maxima there. Treating them reduces the peaks and decay times of modes across the low end.

## Early reflections and the mirror trick

The first reflections from the side walls, ceiling, desk and floor reach your ears a few milliseconds after the direct sound. Because they're close in time and level, they **comb-filter** with it (lesson 1) and blur the stereo image.

**The mirror trick** finds where to put absorption:

1. Sit in the listening position.
2. Have someone slide a mirror flat along the side wall.
3. Wherever you can see a **monitor's tweeter** in the mirror, that's a first-reflection point. Mark it.
4. Repeat for the other wall and the ceiling (with a mirror on a pole, or a laser and some geometry).

Absorbers at those points reduce the strongest early reflections. The desk and the console surface are reflection points too, which is one reason monitors often go on stands behind the desk rather than on it.

## Near-field monitor placement

**Near-field monitors** are designed for short listening distances, often around 1–2 m, which increases direct sound relative to reflected sound. Actual room contribution still depends on the room, directivity and frequency. Placement guidelines, largely as Genelec's placement guide sets them out:

- **Equilateral triangle.** The two monitors and your head form an equilateral triangle: **60° between the monitors**, each aimed at the listening position.
- **Ear height.** The acoustic axis (usually between tweeter and woofer, or as the manual says) at ear level, typically 1.2–1.4 m from the floor for a seated listener. Tilt rather than lifting too high; Genelec suggests no more than about 15° of tilt.
- **Symmetry.** Place the setup symmetrically left–right in the room so both speakers see the same boundaries.
- **Avoid half room height and the room's exact middle**, where modes and floor-ceiling reflections line up badly.

```diagram
        L monitor      R monitor
            \   60 deg   /
             \          /
              \        /
               \      /
                listener
  (equal distances on all three sides)
```

### Wall distance and SBIR

Sound radiates backwards from a monitor at low frequencies (it's omnidirectional there; lessons 4 and 5). That rear sound reflects off the front wall and returns. Where the round trip delays it by half a period, which happens when the distance to the wall is a **quarter wavelength**, it cancels the direct sound: **speaker boundary interference response (SBIR)**.

```
f_notch ≈ c / (4 * d)
# wall-normal path approximation
```

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
- Computes the **impulse response**, and from it the **frequency response**, **waterfall** (how each frequency decays over time, which shows ringing modes clearly) and **decay / RT60** figures.
- Helps identify **room modes** and can calculate EQ filters.

A practical workflow:

1. Measure each monitor separately at the listening position, at a moderate level (lesson 2: protect your ears).
2. Look for big peaks and deep notches below about 300 Hz, and long decay in the waterfall.
3. Move the listening position and speakers first; that changes modes and SBIR far more than EQ can.
4. Add bass traps and first-reflection absorption, and re-measure.
5. Only then use EQ, mainly to **cut peaks**. Don't try to fill deep notches with boost: they're cancellations, and boosting them wastes amplifier power and driver excursion.

## Key takeaways
- Axial room modes sit at f = n·c/(2L); coincident modes from related dimensions can reinforce response peaks depending on excitation and position, and the response depends heavily on seat position.
- Below the Schroeder frequency (≈ 2000·√(RT60/V)) treat the room as modes; above it, as reflections and reverberation.
- Sabine: RT60 = 0.161·V/A, with A = Σ S·α; absorption coefficients vary strongly with frequency.
- Absorbers remove energy (porous types need depth, ideally around a quarter wavelength from the wall); diffusers scatter it; bass traps go in corners.
- Find first-reflection points with the mirror trick and treat them.
- Set monitors in a 60° equilateral triangle at ear height, symmetrically; SBIR notches fall at c/(4d), so mount close to the wall or flush.
- Measure with REW and a calibrated mic: fix placement and treatment first, then cut (don't boost) with EQ.

## Further reading
- [Room modes — Wikipedia](https://en.wikipedia.org/wiki/Room_modes)
- [Room acoustics (frequency zones, Schroeder frequency) — Wikipedia](https://en.wikipedia.org/wiki/Room_acoustics)
- [Reverberation (Sabine's equation) — Wikipedia](https://en.wikipedia.org/wiki/Reverberation)
- [Driving room modes and source location — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/RoomModes/driving.html)
- [Bass trap — Wikipedia](https://en.wikipedia.org/wiki/Bass_trap)
- [How to place your monitors — Genelec](https://www.genelec.com/monitor-placement)
- [Room EQ Wizard (REW)](https://www.roomeqwizard.com/)
- [REW help — Room EQ Wizard](https://www.roomeqwizard.com/help/help_en-GB/html/index.html)
