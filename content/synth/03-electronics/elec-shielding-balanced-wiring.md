---
id: elec-shielding-balanced-wiring
sourceLesson: elec-noise-grounding
title: "Shielding, twisted pairs and balanced audio"
level: advanced
minutes: 1
summary: "Connector shape alone does not establish balanced operation."
---

Connector shape alone does not establish balanced operation.

## Shielded cable and wiring
A **shielded cable** surrounds the signal conductor(s) with a braid or foil connected to ground. The shield intercepts electric-field interference before it reaches the signal.

- **Unbalanced (TS):** one conductor plus shield. The shield is also the signal return, so ground-loop current in it adds to the signal.
- **Balanced wiring (often TRS or XLR):** two signal conductors plus shield. The shield is not the intended audio signal-return conductor, and interference common to both conductors cancels at a balanced input.
- **Twisting** a signal wire with its return reduces magnetic pickup, because each twist reverses the induced voltage.

Inside the build:

- Keep audio wires short and away from digital lines, LED wiring and power.
- Cross noisy wiring at right angles rather than running it alongside audio.
- Run each signal and its own return together.

## Check function as well as connector

A TRS connector may carry unbalanced stereo, balanced mono or another function. It does not make a circuit balanced. A balanced interface needs suitably balanced impedances to ground and a differential receiver with adequate common-mode rejection and input range. Its two output voltages need not always be equal and opposite. Follow both devices’ actual wiring documentation.

## Key takeaways

- Connector shape alone does not establish balanced operation.
- Keep signals close to their own returns and away from noise sources.

## Further reading

- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
- [Analog Devices MT-095: interference and shielding](https://www.analog.com/media/en/training-seminars/tutorials/MT-095.pdf)
