---
id: aud-drivers-motor
title: From voice-coil current to cone force
level: intermediate
minutes: 4
summary: A magnetic field and current-carrying voice coil create force.
sourceLesson: aud-drivers
---

A **loudspeaker driver** is the motor and diaphragm that actually move air. A loudspeaker *system* is one or more drivers plus an enclosure (the enclosure units) and usually a crossover (the crossover units). This lesson is about the driver: how it works, and how to read the numbers on its datasheet.

## The motor structure

Nearly all speakers you will meet are **moving-coil** (electrodynamic) drivers, a design dating from the 1920s.

```diagram
     surround          cone
   ,-----------.  /
  (             )/
   \  +-------+ /      spider
    \ | coil  |/  ===  (suspension)
  [N]=|=gap===|=[N]
  [S]  pole    [S]  <- magnet
       piece
```

The parts:

- **Magnet and pole pieces (the motor).** A permanent magnet (ferrite or neodymium) and steel parts concentrate a strong magnetic field in a narrow ring-shaped **magnetic gap**.
- **Voice coil.** A coil of fine wire wound on a light former, sitting in the gap. It's attached to the cone.
- **Cone (diaphragm).** Pushes the air. Paper, polypropylene, aluminium and composites are common. It must be light and stiff.
- **Driver suspension.** The **driver surround** at the outer edge and the **driver spider** behind the cone keep the coil centred in the gap and provide a restoring force that pulls the cone back to rest.
- **Basket (frame)** holds it all together.

## How current becomes sound

A current in a wire in a magnetic field feels a force (the Lorentz force; it's the motor principle). The voice coil is wound so the wire crosses the field at right angles everywhere in the gap, so the force on it is simply:

```formula essential
F = Bl i
where
F: the force on the voice coil (and so on the cone), in newtons (N)
B: the magnetic flux density in the gap, how strong the magnet's field is there, in tesla (T); around 1 T is typical
l: the length of voice-coil wire sitting in the field, in metres (m); often several metres of fine wire
i: the current through the voice coil, in amperes (A)
Bl: the product of B and l, quoted on datasheets as the "force factor" or "BL", in tesla-metres (T·m); typically about 5–20 T·m
N: newton, the unit of force
T: tesla, the unit of magnetic flux density
m: metre
A: ampere, the unit of current
In words: the push on the cone is proportional to the current in this small-signal model; a stronger field or more wire in the gap gives more push per amp.
```

Datasheets quote the product **Bl** ("BL") because B and l only ever appear together. A 7 T·m driver turns each ampere into about 7 newtons of push. Three consequences follow:

- **The force follows the current**, not the voltage. The amplifier sets a voltage; the driver's impedance (next lesson) decides how much current flows.
- **Audio current alternates, so the force alternates** and the cone moves back and forth, pushing air (the acoustics lessons).
- **The relationship is only linear while the coil stays in the gap.** At large excursions part of the coil leaves the strongest field, so Bl falls and the force no longer follows the current: one source of distortion at high level (a later lesson covers excursion limits).

The cone, coil and the air it carries have **mass**; the surround and spider act as a **suspension spring**. Mass on a spring has a resonance. That's the driver's **free-air resonance, Fs**, one of the Thiele–Small parameters in the enclosure lessons. A heavier cone or a softer suspension lowers Fs. Below Fs the output falls away.

> [!analogy] Real-world analogy: a weight on a rubber band
> Hang a weight from a rubber band and flick it: it bounces at its own natural rate. A heavier weight or a floppier band bounces more slowly. Jiggle your hand slowly and the weight just follows; jiggle near its natural rate and it swings wildly.
>
> **How it maps:** The weight is the moving mass of the cone, coil and air load; the rubber band is the suspension's springiness; the natural bounce rate is Fs. The motor's force is your hand driving the system.
>
> **Where it stops:** A driver's resonance is strongly damped, partly by the suspension and largely by the motor and amplifier acting electrically, so it does not ring on like a bouncing weight. In a box, the trapped air adds a second spring and raises the resonance.

A driver is also an **electromagnetic generator**: a moving coil in a field produces a voltage (back-EMF), exactly as a dynamic mic does. That back-EMF is why the impedance changes so much near resonance.

## Key takeaways
- A magnetic field and current-carrying voice coil create force.
- Moving mass and suspension compliance establish the driver’s free-air resonance.
- The moving coil also generates back electromotive force.

## Further reading
- [Loudspeaker parameters — D. G. Meyer, Purdue](https://engineering.purdue.edu/ece103/LectureNotes/SRS_Loudspeaker_Parameters.pdf)
- [Baffled piston radiation — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/BaffledPiston/BaffledPiston.html)
- [Rated impedance — Dynaudio](https://dynaudio.com/magazine/2023/july/impedance-ask-the-expert)
