---
id: midi-studio-integration-hum-test-session
title: Diagnose ground paths and run a test session
level: advanced
minutes: 3
sourceLesson: midi-studio-integration
summary: Change one signal or low-voltage power connection at a time, preserve protective earth and record the results of stress tests.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Ground loops in a studio setup

A ground loop can form when two devices are connected by more than one conductive ground path, for example through their mains earths **and** an audio cable shield. Interference currents can then create unwanted voltage in signal references, heard as **mains hum** at the mains frequency (50 Hz in the UK) and its harmonics, often with buzz from digital activity.

Common paths in this setup:

- Audio cables (the shield is ground in unbalanced connections).
- **Ordinary USB connections**, which join host and device grounds unless the implementation is electrically isolated. A dev board powered from the computer by USB, with its audio output plugged into the interface (also on that computer), makes a loop through the computer, the interface's USB and the audio cable.
- **Not** DIN MIDI: the optocoupler at each MIDI IN breaks that path, by design.

Diagnose before you fix: unplug one connection at a time and note which change removes the hum. Running a laptop briefly on battery, or temporarily powering the dev board from a different source, can show whether the USB path is involved.

Safe remedies:

- Prefer **balanced** connections into the interface (the Digitakt's outputs are impedance balanced; use TRS cables into balanced line inputs).
- Use **DIN MIDI** rather than USB to connect devices where you can.
- Insert a **ground loop isolator** (an audio isolation transformer) in the offending audio line; it passes the signal while breaking the DC ground path.
- For a USB-powered dev board, a properly specified USB isolator can break the USB ground path if it supports the required speed, class and power arrangement. A separate documented supply plus DIN MIDI may also remove that path; check remaining connections.
- Keep audio cables short and away from power supplies.

> [!warning] Never lift a safety earth
> Removing or taping over the mains earth on a device to stop hum also removes its protection against electric shock. Fix the signal-side ground path instead.

## Putting it together: a first test session

1. Wire the studio connection diagram from **Draw the complete studio connection plan**. Power up with all gains down.
2. Prove MIDI: a MIDI monitor shows the Digitakt track's notes on the expected channel.
3. Prove audio: the synth's test tone reaches the interface meter at a sensible level, with no DC offset and no hum.
4. Sequence a pattern from the Digitakt; record it into Ableton with direct monitoring.
5. Stress test: fast notes, long notes, chords, CC sweeps, pattern stop/start, cable unplug and replug. Record any stuck notes, clicks or dropouts, and their causes, in the project journal.

## Key takeaways
- Change one signal or low-voltage power connection at a time, preserve protective earth and record the results of stress tests.

## Further reading
- [Grounding and shielding audio devices — Rane](https://www.ranecommercial.com/legacy/note151.html)
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
