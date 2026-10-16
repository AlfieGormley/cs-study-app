---
id: midi-synth-handling-stuck-note-defences
title: Prevent and recover from stuck notes
level: intermediate
minutes: 3
sourceLesson: midi-synth-handling
summary: Handle both note endings, channel changes and sustain, then provide a panic action for lost events.
---

## Stuck notes and how to prevent them

A stuck note is a voice that never receives the note off that should end it. The project brief asks for "no unintended stuck notes", so design against each cause.

| Cause | Defence |
|---|---|
| `9n kk 00` not treated as off | Normalise in the parser |
| Note off on another channel | Track notes per channel |
| Channel changed while held | Release all on change |
| Bytes lost (overflow, unplug) | Count overflows; panic |
| Repeated same-key starts | Choose and document a matching policy |
| Sustain pedal held | Defer offs until pedal up |

**Track held notes, not just "the current note".** If the synth remembers only the sounding note, a note off for an earlier key can be misapplied, or missed entirely. A note stack with a documented repeated-key and sustain policy makes those transitions explicit; it does not by itself guarantee that every MIDI use case is covered.

**Implement the mode messages that silence notes.** In supported Omni-Off operation, All Notes Off (CC 123) releases MIDI-started notes on the applicable channel; the specification says to ignore CC 123 while Omni is on. Channel Mode messages are recognised on the configured Basic Channel, and mode changes 124–127 also have the specified note-release effect. The specification says All Notes Off should send voices into their **release** stage rather than cutting them abruptly. All Sound Off (CC 120) is the hard version: silence as soon as possible. A spec detail worth copying: while the sustain pedal (CC 64) is on, note offs **and** All Notes Off are remembered but not acted on until the pedal is released.

**Don't rely on All Notes Off alone.** The specification says receivers aren't required to recognise it, and transmitters should send individual note offs first. Treat it as a safety net.

**Give yourself a panic action.** A button (or a documented MIDI control instruction) that clears held and sustain-deferred notes, silences or releases voices according to its policy, and resets pitch bend to centre is invaluable during development.

**Consider Active Sensing.** If your source sends `FE` and the receiver supports Active Sensing, a receive-activity timeout should silence its voices and leave Active Sensing mode. The nominal interval is 300 ms; the specification recommends a receiver threshold above 330 ms for margin. This detects missing traffic rather than proving the cable physically came out. If the source never sends `FE`, behave normally.

## Key takeaways
- Handle both note endings, channel changes and sustain, then provide a panic action for lost events.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1, including the running status appendix (CCRMA copy)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Polyphony and monophony in instruments: note priority — Wikipedia](https://en.wikipedia.org/wiki/Polyphony_and_monophony_in_instruments)
- [MIDI library for Teensy (serial MIDI) — PJRC](https://www.pjrc.com/teensy/td_libs_MIDI.html)
