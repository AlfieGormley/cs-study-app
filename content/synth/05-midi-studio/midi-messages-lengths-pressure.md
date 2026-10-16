---
id: midi-messages-lengths-pressure
title: Read message lengths and pressure
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: Program Change and Channel Pressure have one data byte; distinguish one pressure value per channel from one per key.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

Note on and note off make a synth play. Everything else in MIDI makes it *expressive* and *in time*: knobs and wheels (control change), patch selection (program change), pitch bend, pressure, the tempo clock, and manufacturer-specific data (SysEx).

This unit maps message lengths and pressure. The following units cover controllers, running status, system messages and MIDI 2.0.

## The full map

Channel messages carry a channel in the low nibble of the status byte (the final placeholder stands for a wire channel from zero to fifteen). System messages (`0xF0`–`0xFF`) have no channel.

| Status | Message | Data bytes |
|---|---|---|
| `8n` | Note Off | key, velocity |
| `9n` | Note On | key, velocity |
| `An` | Poly Key Pressure | key, pressure |
| `Bn` | Control Change | controller, value |
| `Cn` | Program Change | program |
| `Dn` | Channel Pressure | pressure |
| `En` | Pitch Bend | MIDI LSB, MIDI MSB |
| `F0`…`F7` | System Exclusive / Common | varies |
| `F8`…`FF` | System Real-Time | none |

Notice that Program Change and Channel Pressure have **one** data byte; the other channel messages have two. A parser must know this table to tell where one message ends and the next begins.

## Aftertouch (pressure)

Pressing harder on a key after it bottoms out can send:

- **Channel Pressure** `Dn vv`: one value for the whole channel (the MIDI Association's message summary says to send the single greatest pressure of the keys held).
- **Poly Key Pressure** `An kk vv`: a separate value per key.

The receiver decides what pressure does: volume, brightness, vibrato. The Digitakt's MIDI tracks have an "AT" parameter that sends aftertouch to the external synth.

## Key takeaways
- Program Change and Channel Pressure have one data byte; distinguish one pressure value per channel from one per key.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
