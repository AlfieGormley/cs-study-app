---
id: midi-messages-sysex-mode
title: Handle SysEx and channel mode messages
level: intermediate
minutes: 2
sourceLesson: midi-messages
summary: Keep SysEx data seven-bit and respect ID allocation; distinguish channel-wide mode messages from ordinary sound controls.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## System Exclusive

SysEx carries manufacturer-defined data: patch dumps, firmware, parameter edits.

```
F0 <id> <data ...> F7
```

- The ID is 1 byte, or 3 bytes starting with `00`.
- Every SysEx payload byte is a data byte (0–127); independent MIDI real-time status bytes may interleave on the wire. 8-bit data must be packed into 7-bit bytes.
- **ID `7D` is reserved for non-commercial use** (education, research): suitable for a private experiment, not for a product released to the public even free of charge.
- IDs `7E` and `7F` are the **Universal SysEx** messages (7E for Universal Non-Real-Time and 7F for Universal Real-Time) defined by the MIDI specs themselves.
- Only MIDI real-time bytes may be interleaved inside a SysEx message. Any other status byte terminates it, although senders should always end with `F7`.

The Digitakt uses SysEx to send and receive project, pattern and Sound data (presets on the Digitakt II) through its SYSEX DUMP menu, which is a handy backup route.

## Channel mode messages

CC numbers 120–127 are mode messages:

| CC | Meaning |
|---|---|
| 120 | All Sound Off (silence now) |
| 121 | Reset All Controllers |
| 122 | Local Control on/off |
| 123 | All Notes Off |
| 124–127 | MIDI omni mode, MIDI monophonic mode and MIDI polyphonic mode |

Channel Mode messages are recognised on the receiver’s configured Basic Channel, even when Omni is on. MIDI monophonic mode concerns note voices: with Omni off it can allocate one voice per selected MIDI channel; with Omni on it plays one voice across the received channels. MIDI polyphonic mode permits simultaneous voices up to the receiver’s capacity. Neither mode specifies mono or stereo audio output.

All Notes Off and the mode changes also perform the specified note-release functions when supported. In particular, the specification says to ignore CC 123 while Omni is on. All Sound Off silences sound promptly, without waiting for the normal release envelope. Sustain deferral and recovery are developed in the stuck-note unit.

## Key takeaways
- Keep SysEx data seven-bit and respect ID allocation; distinguish channel-wide mode messages from ordinary sound controls.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
