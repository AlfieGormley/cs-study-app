---
id: aud-room-acoustics
title: Room acoustics and monitoring
level: advanced
minutes: 19
summary: Room modes and the axial-mode formula with worked examples, reverberation and RT60 with Sabine's equation, absorption vs diffusion, bass traps, early reflections and the mirror trick, near-field monitor placement (equilateral triangle, wall distance, SBIR), and measuring a room with REW.
---

Put the best monitors in the world in an untreated, square, bare-walled room and you'll hear the room as much as the speakers. Below a few hundred hertz, a small room's response at your listening position can swing by 20 dB or more between neighbouring frequencies. Mix there and you'll correct for problems that only exist in your room, and the mix will sound wrong everywhere else.

This lesson is about understanding what a room does, then placing monitors and treatment so you can trust what you hear.

## Room modes

Between two parallel walls, a sound wave reflects back and forth. At frequencies where a whole number of half-wavelengths fits exactly between the walls, the reflections reinforce each other into a **standing wave**: a **room mode** (or resonance).

To find those frequencies, start from the fact that one half-wavelength, two half-wavelengths, three and so on must fit the gap exactly, then use the link between wavelength, frequency and the speed of sound:

```formula
L = n × λ / 2
λ = c / f_n
f_n = n × c / (2 × L)
where
f_n: the frequency of the nth mode between this pair of walls, in hertz (Hz)
n: the mode number, a whole number 1, 2, 3 …; mode 1 is the lowest (fundamental), mode 2 is twice its frequency, and so on
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
L: the distance between the two parallel walls, in metres (m)
λ: lambda, the wavelength of the sound, in metres (m): the distance one cycle of the wave covers in air
In words: the lowest mode is the frequency whose half-wavelength exactly spans the gap between the walls, and every whole-number multiple of it is a mode too. The bigger the room, the lower the modes.
```

For two walls 5.0 m apart, the first mode is 343 ÷ (2 × 5.0) = 34.3 Hz, the second 68.6 Hz and the third 102.9 Hz. The formula assumes rigid, parallel, flat walls; real walls flex and absorb a little, which damps and slightly shifts the modes.

Those are **axial modes**: between one pair of surfaces. They usually carry the most energy and have the greatest influence on the low-frequency response. **Tangential** modes involve two pairs of surfaces and **oblique** modes all three. For a rectangular (shoebox) room, one formula covers all three kinds:

```formula
f = (c / 2) × √((n_x / L_x)^2
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
f = (343 / 2) × √((1 / 5.0)^2
    + (1 / 3.6)^2)
f ≈ 171.5 × √(0.040 + 0.077)
f ≈ 171.5 × 0.342 ≈ 58.7 Hz
where
f: the frequency of the (1, 1, 0) tangential mode, in hertz (Hz)
√: the square root of the bracket that follows
≈: approximately equal to (values rounded)
Hz: hertz, cycles per second
In words: one half-wavelength along the length and one across the width combine into a mode at about 58.7 Hz, higher than either of the axial modes it combines (34.3 Hz and 47.6 Hz).
```

Like the axial formula, it assumes rigid walls and a perfectly rectangular room.

### Worked example

A small studio of 5.0 × 3.6 × 2.4 m. Using the axial formula for each dimension:

```formula
f_1 = 1 × c / (2 × L)
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
    modes = [round(n * c / (2 * L), 1)
             for n in (1, 2, 3)]
    print(f"{name:<6} {L} m: {modes}")
```

```output
length 5.0 m: [34.3, 68.6, 102.9]
width  3.6 m: [47.6, 95.3, 142.9]
height 2.4 m: [71.5, 142.9, 214.4]
```

Notice that 3.6 ÷ 2.4 = 1.5, so the width's third mode and the height's second land on the **same frequency, 142.9 Hz**. Coincident modal frequencies can produce strong response peaks, depending on how the sources excite them, the listener position and damping. Rooms whose dimensions are simple multiples of each other (a cube is the worst) bunch their modes; unrelated dimensions spread them out more evenly.

What a mode does at your seat depends on **where you sit**:

- For ideal rigid rectangular boundaries, each axial mode has pressure antinodes at its corresponding pair of walls. A general mode may still have nodes along other coordinates on a wall; corners are pressure antinodes of all these ideal modes.
- The first axial mode has a pressure **null** halfway between its walls. At the length midpoint, that ideal mode contributes no pressure; moving away can increase its contribution. The total response also contains direct sound and other modes, so it is not necessarily silent or boomy.
- So bass response varies dramatically with position. This is why many guides suggest avoiding the exact centre of the room for the listening position (Genelec suggests sitting in the front part of the room for music work, and at least 1 m from walls).

### The Schroeder frequency

At low frequencies, modes are few and far apart, and the room behaves like a set of resonances. Higher up, modes overlap so densely that the room behaves statistically, as reverberation. The crossover between the two is often estimated by the **Schroeder frequency**. It needs the room's volume and its reverberation time (RT60, the time sound takes to die away by 60 dB, explained in the next section):

```formula
f_S ≈ 2000 × √(RT60 / V)
where
f_S: the Schroeder frequency, in hertz (Hz): roughly where the room stops acting like separate resonances and starts acting like a smooth reverberant space
≈: approximately equal to; this is a rule-of-thumb estimate, not an exact boundary
2000: a constant that follows from Schroeder's criterion that about three neighbouring modes overlap within each mode's bandwidth (a threshold he chose from measurement experience); it assumes RT60 in seconds and V in cubic metres
√: the square root of the bracket that follows
RT60: the reverberation time, in seconds (s)
V: the room's volume, in cubic metres (m³)
In words: small rooms and long reverberation times push the Schroeder frequency up, so a small studio has a wide band of troublesome modal bass; a large hall's modal region is far below anything you'd hear as a problem.
```

For the treated 43.2 m³ studio worked out below, with an RT60 of 0.44 s:

```formula
f_S ≈ 2000 × √(0.44 / 43.2)
f_S ≈ 2000 × 0.101 ≈ 202 Hz
where
f_S: the Schroeder frequency, in hertz (Hz)
≈: approximately equal to
√: square root
Hz: hertz, cycles per second
In words: in this small treated studio, the room behaves as separate modes below about 200 Hz.
```

The transition is gradual, not a sharp line.

Below it, think **modes** (fix with placement and bass traps). Above it, think **reflections and reverberation** (fix with absorption and diffusion).

## Reverberation and RT60

After a sound stops, its reflections take time to die away. **RT60** is the time for the sound level to fall by **60 dB**. Wallace Sabine's empirical equation (from experiments at Harvard around 1900) relates it to the room's volume and absorption. Use it to estimate how live a room will sound, and how much treatment you'd need to change that:

```formula
RT60 = 0.161 × V / A
A = Σ (S_i × α_i)
where
RT60: the reverberation time, in seconds (s): how long the sound takes to fall by 60 decibels (dB) after the source stops
0.161: Sabine's constant for metric units, in seconds per metre (s/m); it comes from 24 × ln(10) ÷ 343 ≈ 0.161, where 343 m/s is the speed of sound
V: the room's volume, in cubic metres (m³)
A: the room's total absorption, in square metres (m²), also called metric sabins: the area of open window that would absorb the same amount
Σ: sigma, "add up the following for every surface"
i: a counter that runs over the room's surfaces (walls, floor, ceiling, panels)
S_i: the area of surface i, in square metres (m²)
α_i: alpha, the absorption coefficient of surface i: the fraction of sound energy it absorbs on each reflection, from 0 (perfect reflector) to 1 (perfect absorber)
In words: reverberation time grows with the room's volume and shrinks with how much absorbing surface it contains. Double the absorption and you halve RT60.
```

So **A** is each surface's area times its **absorption coefficient** α, summed. Worked through for the 5.0 × 3.6 × 2.4 m studio with bare surfaces averaging α = 0.10, then with 10 m² of surface swapped for panels with α = 0.90:

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
- **Sabine assumes a fairly live room with diffuse sound.** In very absorbent rooms it overestimates RT60 (the Eyring equation is more accurate there), and in small rooms below the Schroeder frequency "reverberation time" is a rough description at best.

Control rooms are typically much drier than living rooms; recommended targets vary by standard and room size, so treat any single number as a guide.

## Absorption vs diffusion

- **Absorbers** convert sound energy to heat. **Porous absorbers** (mineral wool, fibreglass, thick acoustic foam) work by friction as air moves through them. They're most effective where the air particle velocity is high, which is about a **quarter wavelength from a hard wall**. A thin porous panel against a rigid wall generally absorbs low frequencies poorly (the quarter-wavelength rule below puts numbers on this). An air gap can improve lower-frequency absorption.
- **Diffusers** scatter sound in many directions without removing much energy. They break up strong specular reflections and flutter echo (rapid repeats between parallel hard walls) while keeping the room feeling live. They need to be large compared with the wavelengths they diffuse, so they work mainly in the mids and highs, and need some distance from the listener.

A good control room usually combines both: absorption where early reflections hit, diffusion or a mix at the back, and bass trapping in the corners.

### The quarter-wavelength rule

At a hard wall the air can't move, so the air's particle velocity is zero there and rises to a maximum a quarter of a wavelength out. To see which frequency a porous layer of a given depth (or air gap) reaches, set its distance from the wall equal to a quarter wavelength:

```formula
d = λ / 4
λ = c / f
f = c / (4 × d)
f = 343 / (4 × 0.10) ≈ 858 Hz
where
d: the distance from the hard wall to where the absorber material sits, in metres (m); here 10 cm = 0.10 m
λ: lambda, the wavelength, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s)
f: the frequency whose quarter wavelength equals d, in hertz (Hz)
≈: approximately equal to
Hz: hertz, cycles per second
In words: a porous absorber reaches its velocity-maximum position for frequencies whose quarter wavelength fits between it and the wall; the deeper the material or its air gap, the lower that frequency.
```

So a 10 cm panel corresponds to about 850 Hz, and reaching 60 Hz would need about 343 ÷ 240 ≈ 1.4 m. This is a rough guide, not a cut-off or a prediction of measured absorption: material flow resistance, thickness, mounting and the angle the sound arrives at all matter, and a panel still absorbs something below this frequency.

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

The reflected sound travels to the wall and back, an extra distance of twice the speaker-to-wall gap. The first cancellation happens when that extra distance is half a wavelength, so the wave comes back upside down:

```formula
2 × d = λ / 2
λ = c / f_notch
f_notch ≈ c / (4 × d)
f_notch ≈ 343 / (4 × 0.5) ≈ 172 Hz
where
f_notch: the frequency of the first (lowest) cancellation notch, in hertz (Hz)
d: the distance from the speaker's acoustic source to the wall behind it, in metres (m); here 0.5 m
λ: lambda, the wavelength, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s)
≈: approximately equal to; this simple model only counts the straight-back-and-forth path
Hz: hertz, cycles per second
In words: the notch sits at the frequency whose quarter wavelength equals the speaker-to-wall distance, so moving the speaker closer to the wall pushes the notch up in frequency.
```

This assumes the wall is rigid and the reflection travels straight back (the wall-normal path). Real notches are shallower than a perfect cancellation and are partly filled by other paths. The same calculation for other distances:

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
- Axial room modes sit at whole-number multiples of the speed of sound divided by twice the wall spacing; coincident modes from related dimensions can reinforce response peaks depending on excitation and position, and the response depends heavily on seat position.
- Below the Schroeder frequency (about 200 Hz in a small treated studio) treat the room as modes; above it, as reflections and reverberation.
- Sabine's equation: reverberation time is proportional to room volume divided by total absorption (surface area times absorption coefficient, summed); absorption coefficients vary strongly with frequency.
- Absorbers remove energy (porous types need depth, ideally around a quarter wavelength from the wall); diffusers scatter it; bass traps go in corners.
- Find first-reflection points with the mirror trick and treat them.
- Set monitors in a 60° equilateral triangle at ear height, symmetrically; the first SBIR notch falls where the speaker-to-wall distance is a quarter wavelength, so mount close to the wall or flush.
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
