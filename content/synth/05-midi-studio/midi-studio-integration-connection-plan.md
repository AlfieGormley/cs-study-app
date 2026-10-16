---
id: midi-studio-integration-connection-plan
title: Draw the complete studio connection plan
level: advanced
minutes: 4
sourceLesson: midi-studio-integration
summary: Name the exact equipment, identify every MIDI/audio/power path and mark the USB host.
---

The project's success criteria say an external device should play the instrument, its audio should be recorded into Ableton through the existing interface, and a test session should run without stuck notes or audio interruptions. This lesson pulls the module together into that studio setup. It also covers the roadmap's stage 5 exercise: draw the connection diagram and identify MIDI, audio, power and any USB host.

> [!warning] Which Digitakt, and when checked
> Product facts here come from Elektron's official manuals, checked on **16 October 2026**: the **Digitakt** (original) user manual for **OS 1.53**, and the **Digitakt II** user manual for **OS 1.17**. Ports, menus and specifications change between models and OS versions. **Find out which model you own and confirm every port and setting against the current manual for it** before buying parts or wiring anything.

## The two Digitakts at a glance

Both models have the same set of rear connections, with some differences:

| Rear connector | Notes (both models) |
|---|---|
| DC In | 12 V DC, centre positive |
| USB | USB-B, to a computer host |
| MIDI IN | DIN |
| MIDI OUT / SYNC A | MIDI, or DIN sync |
| MIDI THRU / SYNC B | Thru, or DIN sync |
| IN L/R | 1/4″ audio inputs |
| OUT L/R | 1/4″, impedance balanced |
| Headphones | 1/4″ TRS stereo |

Differences that matter here, from each manual's technical information:

| | Digitakt | Digitakt II |
|---|---|---|
| MIDI tracks | 8 dedicated (9–16) | Any of 16 tracks |
| CCs per MIDI track | 8 assignable | 16 assignable |
| Main out max | +22 dBu peak | +18 dBu peak |
| Inputs | Unbalanced, 11 kΩ | Balanced, 21 kΩ |
| USB | Listed as isolated | Hi-speed USB 2.0 |

Both run 48 kHz, 24-bit converters and can be class-compliant USB audio and MIDI devices (USB CONFIG: OVERBRIDGE, USB MIDI, or USB AUDIO/MIDI).

## Step 1: draw the connection diagram

Start from the roadmap's question: for every cable, what does it carry, and who is the USB host? Here is one sensible first design:

```diagram
 DIGITAKT              DIY SYNTH
 MIDI OUT ----DIN----> MIDI IN
 OUT L/R               AUDIO OUT
    |                     |
    v                     v
 AUDIO INTERFACE line inputs
    |
    | USB (interface = device)
    v
 COMPUTER + ABLETON (USB host)
```

And the same design as a cable list, which belongs in your project docs:

| Cable | Carries | Notes |
|---|---|---|
| DT MIDI OUT → synth IN | MIDI | DIN, isolated |
| Synth out → interface in | Audio | Line level |
| DT OUT L/R → interface | Audio | Balanced TRS |
| Interface → computer | USB audio | Computer hosts |
| DT USB → computer | Optional | MIDI/Overbridge |
| Power: each device | DC | Own supply |

Why these choices:

- **DIN MIDI from the Digitakt** works with no computer (this example supports standalone use; whether that is required remains an open project decision), needs no USB host, and is galvanically isolated.
- **The computer is the only USB host.** The interface and the Digitakt are USB devices; so is your dev board if it's on USB. Nothing in the diagram expects two devices to talk directly.
- **The Digitakt's audio** can reach Ableton through the interface (as drawn), or over USB as a class-compliant audio device or via Overbridge, which frees two interface inputs.
- **Power**: the Digitakt uses its own 12 V supply (the documented PSU-3, PSU-3b or PSU-3c supplies for the original and PSU-3c for the II). Your synth should have a suitable, documented low-voltage supply. During development a dev board is often powered over USB from the computer; that connects its ground to the computer's, which matters in the later **Diagnose ground paths and run a test session** unit.

Elektron labels these published maximum ratings “dBu peak”. The standard dBu voltage reference is RMS-based; the manufacturer label is quoted here rather than silently converted into waveform peak volts. Confirm the test/measurement convention and permitted input voltage when comparing equipment.

## Key takeaways
- Name the exact equipment, identify every MIDI/audio/power path and mark the USB host.

## Further reading
- [Digitakt II user manual (OS 1.17) — Elektron](https://www.elektron.se/wp-content/uploads/2026/10/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf)
- [Digitakt user manual (OS 1.53) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
- [Digitakt II support and downloads — Elektron](https://www.elektron.se/support-downloads/digitakt-ii)
- [Live 12 manual: Routing and I/O (monitoring, external instruments) — Ableton](https://www.ableton.com/en/live-manual/12/routing-and-i-o/)
- [Live 12 manual: External Instrument device — Ableton](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Live 12 manual: Synchronizing with Link, Tempo Follower and MIDI — Ableton](https://www.ableton.com/en/live-manual/12/synchronizing-with-link-tempo-follower-and-midi/)
- [Ground loop (electricity) — Wikipedia](https://en.wikipedia.org/wiki/Ground_loop_(electricity))
