---
id: midi-messages-midi-two-scope
title: Place MIDI 2.0 in the project
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: UMP and higher-resolution messages extend the ecosystem; choose supported transports and features for the actual devices.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## MIDI 2.0 in one section

MIDI 2.0 (announced in January 2020, core specifications updated in June 2023) **extends** MIDI 1.0 rather than replacing it. The headline changes, from the MIDI Association:

- The **Universal MIDI Packet (UMP)** replaces the byte stream with 32-, 64-, 96- or 128-bit packets. UMP can carry both MIDI 1.0 and MIDI 2.0 messages, organised as 16 groups of 16 channels.
- **Higher resolution**: velocity is 16-bit; control changes, pressure and pitch bend are 32-bit.
- **Per-note** controllers and pitch, and thousands of additional registered and assignable controllers.
- **MIDI-CI** (Capability Inquiry) lets two devices discover each other's features. Profiles and Property Exchange (JSON-based) build on it.
- Optional **Jitter Reduction timestamps**.
- **USB MIDI 2.0** carries UMP natively and can fall back to USB MIDI 1.0.

For the documented DIN connection in this example, MIDI 1.0 is a practical initial target; this does not select the project's final hardware or architecture. The Digitakt manuals describe MIDI 1.0 facilities (notes, CC, NRPN, program change, clock), and DIN MIDI carries the MIDI 1.0 byte stream. MIDI 2.0 becomes interesting if you later want very high-resolution or per-note control from a computer over USB.

## Key takeaways
- UMP and higher-resolution messages extend the ecosystem; choose supported transports and features for the actual devices.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
