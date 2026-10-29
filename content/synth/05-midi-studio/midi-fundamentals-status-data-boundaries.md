---
id: midi-fundamentals-status-data-boundaries
title: Recognise status and data bytes
level: basic
minutes: 2
sourceLesson: midi-fundamentals
summary: The top bit distinguishes status from seven-bit data; discard orphan data and preserve interrupted messages around MIDI real-time bytes.
---

## Status bytes and data bytes

Every MIDI 1.0 byte is one of two kinds, and you can tell which by looking at the top bit:

```
bit:   7 6 5 4 3 2 1 0
status 1 t t t c c c c   0x80-0xFF
data   0 v v v v v v v   0x00-0x7F
```

- A **status byte** has bit 7 set. It says what kind of message this is. For channel messages, the top four bits (`tttt` above, including the 1) are the message type and the bottom four (`cccc`) are the channel.
- A **data byte** has bit 7 clear, so it carries a value from **0 to 127** (7 bits).

Why 128 values? Each bit doubles the number of possible patterns. Seven free bits give 128 patterns, numbered 0 to 127; all eight bits would give 256. Spending the top bit on the status/data flag is what halves the range.

This one-bit rule is what makes MIDI robust. If a receiver joins mid-stream or loses a byte, a status byte outside the MIDI real-time class supplies a new message boundary. Real-time bytes also have bit 7 set but may interleave with a message without resetting it.

Channel messages have one or two data bytes according to their status, and a receiver waits for that complete message before dispatching it. System messages differ: some have no data bytes, while SysEx has variable length. The specification also says receivers should ignore data bytes that are not preceded by a valid status byte, apart from one shortcut called running status, which the later running-status unit covers.

## Key takeaways
- Bit 7 set means status (0x80–0xFF); bit 7 clear means data (0x00–0x7F), so data values run 0–127.
- Any status byte outside the real-time class (0xF8–0xFF) ends the previous message context, which lets a receiver resynchronise after joining mid-stream.
- Discard data bytes that arrive with no status to attach to, and let MIDI real-time bytes pass without disturbing a half-finished message.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
