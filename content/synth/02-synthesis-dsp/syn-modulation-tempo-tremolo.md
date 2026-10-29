---
id: syn-modulation-tempo-tremolo
title: Tempo sync and tremolo gain
level: intermediate
minutes: 3
summary: Tempo sync and tremolo gain.
sourceLesson: syn-modulation
---

Two common LFO options:

- **Key sync / retrigger:** reset the LFO phase on each note so every note starts its wobble the same way. Without it, a free-running LFO’s phase at note-on depends on timing and can differ between notes.
- **Tempo sync:** derive the rate from tempo. When the tempo beat is a quarter note, 120 BPM gives half a second per quarter note, so one cycle per quarter note is 2 Hz. A time signature or tempo marking can assign another note value to the beat; state that convention.

The tempo-sync conversion in general:

```formula reference
r = (BPM / 60) / L
where
r: the LFO rate, in hertz (Hz): cycles per second
BPM: the tempo in beats per minute; dividing by 60 gives beats per second
L: the length of one LFO cycle, in beats: 1 for a quarter note (one beat in 4/4 time), 0.5 for an eighth note, 4 for a bar of 4/4
Hz: hertz
In words: Convert tempo to beats per second, then divide by the number of beats assigned to each LFO cycle. Shorter note divisions run faster at the same tempo.
```

**Gain depth** is usually specified as a fraction of the level (or in dB). Apply it like this:

With a unipolar LFO, subtract a scaled amount from unity gain. Zero depth leaves the signal unchanged; full depth reaches silence at the LFO maximum. Intermediate depths reduce level without raising the original peak.

That keeps the peak at the original level and avoids pushing the signal past full scale.

## Key takeaways

- State which note value receives the tempo beat before deriving an LFO rate.
- Unipolar tremolo can reduce level without increasing the original peak.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
