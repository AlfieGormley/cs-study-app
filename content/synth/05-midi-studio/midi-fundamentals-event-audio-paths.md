---
id: midi-fundamentals-event-audio-paths
title: Separate MIDI events from audio
level: basic
minutes: 2
sourceLesson: midi-fundamentals
summary: Keep a distinct path for MIDI instructions and for the sound the synth creates.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

MIDI (Musical Instrument Digital Interface) lets a sequencer such as a Digitakt tell your synth what to play. These lessons concentrate on MIDI 1.0 performance messages and the separate audio signal route.

The most important idea in this lesson is also the simplest: **MIDI note events do not carry live audio.** MIDI also supports specialised SysEx transfers, including sample data, but that is distinct from an audio stream. It carries short messages such as "key 60 went down on channel 1, quite hard" and "key 60 came back up". The receiving instrument decides what those events sound like.

## Events, not audio

MIDI describes *what was played and when*; audio is the sound itself. The table sets them side by side.

> [!analogy] Real-world analogy: a player-piano roll
> A player-piano roll is a strip of paper with holes punched where keys should go down. Feed the same roll into two different pianos and you hear two different instruments playing the same notes.
>
> **How it maps:** the holes are MIDI note events (which key, when it starts and stops), and the piano that reads the roll is your synth, which creates the actual sound. Swapping the synth patch is like swapping the piano: the events stay the same, the sound changes.
>
> **Where it stops:** a roll is read mechanically in one fixed order, whereas MIDI messages arrive live, carry extra values such as velocity and channel, and can include controllers, clock and SysEx data. A roll also produces no electrical signal, so it says nothing about the separate audio cable your synth still needs.

| | MIDI | Audio |
|---|---|---|
| Carries | Performance events here | Audio waveform |
| Size | Often 2–3 MIDI 1.0 bytes | For example 48,000 digital samples/s |
| Sound depends on | Receiver's synthesis | Recorded waveform and playback chain |
| Cable | MIDI (DIN, TRS, USB) | Audio jack, USB audio |

This has practical consequences for your build:

- Your synth needs **two separate paths**: MIDI in (what to play) and audio out (the sound it makes). Connecting the Digitakt's MIDI OUT to your synth does nothing audible until your synth's audio output reaches a mixer or interface.
- A recorded MIDI part in Ableton is a list of events. Change the synth patch and the "recording" sounds different. A recorded audio part is fixed.
- A complete MIDI 1.0 Note On uses three bytes before transport framing. Digital audio storage depends on duration, sample rate, channel count and sample representation; it is usually far larger than the event list.

## Key takeaways
- MIDI note messages are short event descriptions (key, velocity, timing), not a sound waveform.
- The receiving instrument decides what the events sound like, so a recorded MIDI part changes when the patch changes.
- Keep a distinct path for MIDI instructions and for the sound the synth creates, and check each path separately when something is silent.

## Further reading
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [MIDI tuning standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [Live 12 manual: Editing MIDI — Ableton](https://www.ableton.com/en/live-manual/12/editing-midi/)
- [Digitakt user manual (OS 1.53; MIDI track note range) — Elektron](https://www.elektron.se/wp-content/uploads/2026/09/Digitakt-User-Manual_ENG_OS1.53_260909.pdf)
