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
| `0xFB` | Continue |
| `0xFC` | Stop |
| `FE` | Active Sensing |
| `FF` | System Reset |

`F9` and `FD` are undefined and should be ignored.

**Timing Clock is sent 24 times per quarter note** (24 PPQN, pulses per quarter note). A receiver measures the gap between clocks to find the tempo. Going the other way, the expected gap at a given tempo is one minute divided by the number of clocks in that minute:

```formula
t_clk = 60 s / (BPM × PPQN)
t_clk = 60 s / (120 × 24)
t_clk = 60 s / 2880
t_clk ≈ 0.020833 s ≈ 20.833 ms
where
t_clk: the time between consecutive Timing Clock (F8) bytes, in seconds (s) or milliseconds (ms)
BPM: tempo in beats (quarter notes) per minute; 120 here
PPQN: pulses per quarter note, fixed at 24 for MIDI clock
60 s: the number of seconds in a minute
s: seconds
ms: milliseconds, thousandths of a second
≈: approximately equal to (rounded)
In words: at 120 BPM there are 2,880 clocks a minute, so one arrives roughly every 20.8 ms.
```

Faster tempos give shorter gaps: at 60 BPM the gap is about 41.7 ms. A receiver can turn the formula round (the tempo in BPM is 60 seconds divided by 24 times the measured gap) to estimate tempo; in practice it averages several gaps, because individual clocks jitter. The same calculation in Python:

```python
def clock_interval_ms(bpm, ppqn=24):
    # Treat one beat as a quarter note here.
    beats_per_s = bpm / 60
    # Convert seconds per tick to
    # milliseconds.
    return 1000 / (beats_per_s * ppqn)

for bpm in (60, 120, 140):
    ms = clock_interval_ms(bpm)
    print(bpm, round(ms, 3))
```

```output
60 41.667
120 20.833
140 17.857
```

Six clocks make one sixteenth note, which is the unit the **Song Position Pointer** (`F2 ll mm`) counts in. Transport details from the specification:

- **Start** (`FA`) means play from the beginning. **Continue** (`0xFB`) means resume from the current position. A synced receiver starts on the *next* `F8` after either, and the specification asks senders to leave at least 1 ms between `FA` and the first `F8`.
- **Stop** (`0xFC`) should stop playback immediately.
- Clocks may keep flowing while stopped, so receivers can lock to tempo before Start.

**Active Sensing** (`FE`) is optional. Once a receiver has seen it, it should expect some message at least every 300 ms. If all MIDI traffic stops for the timeout, it should silence its voices and leave Active Sensing mode; silence can indicate disconnection, but does not prove the physical cause. The detailed specification recommends sending within 270 ms and judging loss after more than 330 ms to leave timing margin around the nominal 300 ms interval.

A simple mono synth needs clock only for tempo-synced features such as an arpeggiator or a synced LFO. It must still *tolerate* clock bytes, because a sequencer like the Digitakt may send them constantly.

## Key takeaways
- MIDI clock has 24 ticks per quarter note; transport and optional Active Sensing have distinct jobs.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
