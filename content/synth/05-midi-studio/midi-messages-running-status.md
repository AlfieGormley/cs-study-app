---
id: midi-messages-running-status
title: Preserve and clear running status
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: Reuse only channel status; System Common and SysEx clear it, while MIDI real-time bytes leave it and partial messages intact.
---

## Running status

Running status is a byte-saving rule for **channel voice and mode messages**: once a status byte has been sent, the transmitter can omit it for following messages of the same type and channel, and send only the data bytes.

```
full:     90 3C 64  90 40 64  90 43 64
running:  90 3C 64     40 64     43 64
```

Nine bytes become seven. Combined with "note on, velocity 0 = note off", a whole melody can go out with a single `90` at the start.

The receiver's rules, from the specification and its appendix:

1. Remember the last channel status byte in a **running status buffer**.
2. A data byte that arrives when a complete message has just ended reuses that status.
3. Any new channel status byte replaces it.
4. **System Exclusive and System Common** status bytes clear it.
5. **Real-time bytes do not touch it**, even when they arrive between data bytes.

Running status is optional for transmitters but mandatory for receivers. The parser state-machine unit turns these rules into executable code.

## Key takeaways
- Reuse only channel status; System Common and SysEx clear it, while MIDI real-time bytes leave it and partial messages intact.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
