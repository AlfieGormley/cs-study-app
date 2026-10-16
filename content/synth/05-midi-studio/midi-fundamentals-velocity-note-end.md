---
id: midi-fundamentals-velocity-note-end
title: Handle velocity and both note endings
level: basic
minutes: 2
sourceLesson: midi-fundamentals
summary: Normalise Note On with velocity zero into a note-off event before voice handling.
---

Velocity and note endings are separate from the key number. The synth must recognise both documented ways to release a MIDI note.

## Velocity


For a Note On that starts a note, velocity is a seven-bit performance value from 1 to 127, commonly representing how fast a key was struck. The specification leaves its interpretation to the receiver; it suggests that if velocity controls loudness, the mapping should preferably be exponential, and that devices without velocity sensing should send **64**.

### Note on with velocity 0 means note off

This rule trips up nearly every first MIDI implementation. The MIDI 1.0 specification gives two equivalent ways to end a note:

1. A Note Off message: `8n kk vv`.
2. A Note On message with velocity zero: `9n kk 00`.

It says a receiver **must be able to recognise either method, and should treat them identically**. Many transmitters prefer the second form because, combined with running status, a long run of notes can be sent without repeating the status byte.

If your synth treats `9n kk 00` as "start a note very quietly", notes will never end. That is a classic stuck-note bug.

## Key takeaways
- Normalise Note On with velocity zero into a note-off event before voice handling.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
