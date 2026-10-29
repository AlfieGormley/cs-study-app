---
id: midi-fundamentals-channel-nibbles
title: Encode the MIDI channel
level: basic
minutes: 2
sourceLesson: midi-fundamentals
summary: Convert displayed channels to a zero-based low nibble when sending, and add one when displaying received channels.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Channels

MIDI 1.0 has **16 channels**. They let one cable address up to 16 independent instruments (or parts of a multitimbral instrument). Each receiver is set to listen on one channel (or all of them, "omni") and ignores channel messages for others.

The channel lives in the low nibble (the bottom four bits) of the status byte, numbered 0–15 on the wire. People and manuals number channels 1–16. To build a channel message's status byte, take the message type's base value, whose low nibble is zero, and drop the wire channel number into that empty nibble:

```formula essential
S = T + (ch − 1)
where
S: the status byte that goes on the wire, written in hexadecimal (0x…)
T: the message type's base value, with its low nibble zero: 0x80 Note Off, 0x90 Note On, 0xB0 Control Change
ch: the channel as people and manuals number it, 1 to 16; subtracting 1 gives the 0–15 wire number
In words: the top nibble says what kind of message it is and the bottom nibble holds the channel minus one, so a Note On for channel 10 is 0x99, not 0x9A.
```

This off-by-one causes real bugs:

```
user channel  1  -> nibble 0x0
user channel 10  -> nibble 0x9
user channel 16  -> nibble 0xF
```

> [!warning] Channel 1 is 0 on the wire
> When the Digitakt's MIDI track is set to CHAN 1, your synth will see status bytes with channel nibble 0 (for example `0x90` for a note on), not nibble 1 (`0x91`). Store channels internally as 0–15 and add 1 only when displaying them.

## Key takeaways
- MIDI 1.0 has 16 channels, carried in the low nibble of each channel message's status byte.
- The wire counts channels 0–15 while people count 1–16: subtract one when sending and add one only when displaying.
- A receiver that "doesn't respond" is often listening on the wrong nibble; check the raw status byte in a MIDI monitor.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
