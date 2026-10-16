---
id: midi-messages-control-change-map
title: Choose and decode control changes
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: Check the published CC allocation and document the numbers your synth accepts.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Control change

`Bn cc vv`: controller number `cc` (0–119) set to value `vv` (0–127). Controllers 120–127 use the same status byte but are **Channel Mode messages** (covered in **Handle SysEx and channel mode messages**).

Commonly met controllers, from the MIDI Association's control change table:

| CC | Defined as |
|---|---|
| 0 / 32 | Bank Select MIDI MSB / MIDI LSB |
| 1 | Modulation wheel |
| 7 | Channel Volume |
| 10 | Pan |
| 11 | Expression |
| 64 | Sustain pedal (≤63 off, ≥64 on) |
| 71 | Sound Ctrl 2 (default: timbre) |
| 72 / 73 | Sound Ctrl 3 / 4 (release / attack) |
| 74 | Sound Ctrl 5 (default: brightness) |

Many synths map CC 74 to filter cutoff and CC 71 to resonance, following those "brightness" and "timbre" defaults, but nothing forces this. Plenty of CC numbers (for example 20–31 and 102–119) are listed as **undefined**, which makes them a sensible home for your synth's own parameters. Whatever you choose, document it in a table: the specification asks manufacturers to publish a controller allocation table, and you will need it yourself when setting up the Digitakt.

## Key takeaways
- Check the published CC allocation and document the numbers your synth accepts.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
