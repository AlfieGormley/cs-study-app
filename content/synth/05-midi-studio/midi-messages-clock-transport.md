---
id: midi-messages-clock-transport
title: Interpret clock, transport and sensing
level: intermediate
minutes: 4
sourceLesson: midi-messages
summary: MIDI clock has 24 ticks per quarter note; transport and optional Active Sensing have distinct jobs.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## System real-time: clock and transport

Real-time messages are single status bytes with no data. They may appear **anywhere**, even in the middle of another message, so they can keep accurate time.

| Byte | Message |
|---|---|
| `F8` | Timing Clock |
| `FA` | Start |
| `FB` | Continue |
| `FC` | Stop |
| `FE` | Active Sensing |
| `FF` | System Reset |

`F9` and `FD` are undefined and should be ignored.

**Timing Clock is sent 24 times per quarter note** (24 PPQN, pulses per quarter note). The number of clocks per beat never changes, so the *gap* between clocks carries the tempo: faster tempo, shorter gaps. At 120 BPM a clock arrives about every 20.8 ms; halve the tempo to 60 BPM and the gap doubles to about 41.7 ms.

```formula reference
t_clk = 60 s / (BPM × PPQN)
where
t_clk: the time between consecutive Timing Clock (F8) bytes, in seconds (s)
BPM: tempo in beats (quarter notes) per minute
PPQN: pulses per quarter note, fixed at 24 for MIDI clock
60 s: the number of seconds in a minute
s: seconds
In words: one minute divided by the number of clocks sent in that minute gives the gap between clocks; at 120 BPM that is about 20.8 ms.
```

A receiver works the other way round: it measures the gaps and infers the tempo. Individual clocks jitter (for example when a clock byte has to wait behind another byte on DIN), so a tempo estimate averages several gaps rather than trusting one.

Six clocks make one sixteenth note, which is the unit the **Song Position Pointer** (`F2 ll mm`) counts in. Transport details from the specification:

- **Start** (`FA`) means play from the beginning. **Continue** (`FB`) means resume from the current position. A synced receiver starts on the *next* `F8` after either, and the specification asks senders to leave at least 1 ms between `FA` and the first `F8`.
- **Stop** (`FC`) should stop playback immediately.
- Clocks may keep flowing while stopped, so receivers can lock to tempo before Start.

**Active Sensing** (`FE`) is optional. Once a receiver has seen it, it should expect some message at least every 300 ms. If all MIDI traffic stops for the timeout, it should silence its voices and leave Active Sensing mode; silence can indicate disconnection, but does not prove the physical cause. The detailed specification recommends sending within 270 ms and judging loss after more than 330 ms to leave timing margin around the nominal 300 ms interval.

A simple mono synth needs clock only for tempo-synced features such as an arpeggiator or a synced LFO. It must still *tolerate* clock bytes, because a sequencer like the Digitakt may send them constantly.

## Key takeaways
- MIDI clock is 24 `F8` bytes per quarter note; tempo is carried by the gap between them, so a receiver averages gaps to estimate it.
- Start, Continue and Stop control transport; a synced receiver starts on the next clock after Start or Continue.
- Active Sensing is optional, but once seen it means "expect traffic at least every 300 ms"; every receiver must tolerate clock bytes even if it ignores them.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
