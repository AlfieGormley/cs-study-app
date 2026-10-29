---
id: syn-synthesis-overview-voice-flow
title: Audio and control in one voice
level: basic
minutes: 3
summary: Audio and control in one voice.
sourceLesson: syn-synthesis-overview
---

## The classic subtractive voice

A **voice** is everything needed to play one note. The textbook subtractive voice looks like this:

```diagram
 note pitch
     |
     v
 +-------+   +--------+   +-------+
 |  OSC  |-->| FILTER |-->|  AMP  |--> out
 +-------+   +--------+   +-------+
     ^            ^           ^
     |            |           |
    LFO      filter env    amp env
             (+ velocity)  (gate)
```

- **Oscillator (VCO/DCO):** generates a periodic waveform at the note's pitch.
- **Filter (VCF):** usually a resonant low-pass; its cutoff sets brightness.
- **Amplifier (VCA):** multiplies the signal by a gain, so the note can start and stop.
- **Envelopes:** time-varying control signals started by the key (the *gate*). One drives the amplifier, another typically sweeps the filter cutoff.
- **LFO:** a slow oscillator (below about 20 Hz) that wobbles pitch (vibrato), level (tremolo) or cutoff.

The "V" names come from analogue gear where each block was *voltage controlled*. In software the same structure holds: audio flows left to right, and control signals arrive from below.

Notice there are two kinds of signal. **Audio signals** run at the sample rate and you hear them. **Control signals** (envelopes, LFOs, knob positions, MIDI) steer the audio blocks. They often change more slowly, but fast modulation can require per-sample updates too. Keeping these separate is central to real-time design, as later lessons show.

## Key takeaways

- Follow audio through oscillator, filter and amplifier.
- Envelopes, LFOs and note events control those blocks.

## Further reading

- [Minimoog Model D user guide — Moog](https://cdn.inmusicbrands.com/Moog/Model%20D/Minimoog_Model_D_Manual.pdf)
- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
