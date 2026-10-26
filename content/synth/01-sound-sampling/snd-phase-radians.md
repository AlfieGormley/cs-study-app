---
id: snd-phase-radians
title: Phase and radians
level: basic
minutes: 3
summary: Measure position within a cycle and explain reinforcement, cancellation and phase jumps.
sourceLesson: snd-waves
---

## Phase and radians

The **phase of a wave** says *where in its cycle* it is at a given moment. You can measure it in fractions of a cycle (0 to 1), degrees (0° to 360°), or **radians** (0 to 2π). Maths libraries use radians, so get comfortable with them.

A radian measures an angle by comparing arc length with circle radius. One full turn is about 6.283 radians. Cycle fractions, degrees and radians are three units for the same position:

| Cycles | Degrees | Radians |
|---|---|---|
| 0.25 | 90° | π/2 ≈ 1.571 |
| 0.5 | 180° | π ≈ 3.142 |
| 1 | 360° | 2π ≈ 6.283 |

Phase matters most when you **combine** waves. Two identical sines in phase add up to double the amplitude. Shift one by half a cycle (π radians, 180°) and they cancel completely. Anywhere in between gives partial reinforcement or partial cancellation. That's why detuned oscillators "beat", and why some layered sounds go thin when a phase relationship shifts.

Phase on its own, for a single steady tone, is mostly inaudible. Your ear can't tell a sine from the same sine starting a quarter-cycle later. What you *can* hear is a sudden phase **jump** in the middle of a tone: the waveform can jump to a new value instantly, creating a click. A phase change at a specially chosen point can leave the value unchanged, so a click is not inevitable.

## Pitfalls

- **Degrees passed to `sin`.** If phase is in degrees, convert it with `math.radians` before calling `math.sin`. A quarter-cycle should reach the positive peak, rather than an arbitrary value.

## Key takeaways

- One full cycle is 2π radians; maths-library sine functions expect radians.
- Relative phase controls how two waves reinforce or cancel.
- A sudden phase change can create a discontinuity and a click.

## Further reading

- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Phase (waves) — Wikipedia](https://en.wikipedia.org/wiki/Phase_(waves))
