---
id: syn-modulation-tempo-tremolo
title: Tempo sync and tremolo gain
level: intermediate
minutes: 3
summary: Tempo sync and tremolo gain.
sourceLesson: syn-modulation
---

Two common LFO options:

- **Key sync / retrigger:** reset the LFO phase on each note so every note starts its wobble the same way. Free-running LFOs drift relative to the notes.
- **Tempo sync:** derive the rate from tempo. When the tempo beat is a quarter note, 120 BPM gives half a second per quarter note, so one cycle per quarter note is 2 Hz. A time signature or tempo marking can assign another note value to the beat; state that convention.

The tempo-sync conversion in general:

```formula
r = (BPM / 60) / L
r = (120 / 60) / 1 = 2 Hz
r = (90 / 60) / 0.5 = 3 Hz
where
r: the LFO rate, in hertz (Hz): cycles per second
BPM: the tempo in beats per minute; dividing by 60 gives beats per second
L: the length of one LFO cycle, in beats: 1 for a quarter note (one beat in 4/4 time), 0.5 for an eighth note, 4 for a bar of 4/4
Hz: hertz
In words: turn the tempo into beats per second, then divide by how many beats one LFO cycle should last.
```

**Gain depth** is usually specified as a fraction of the level (or in dB). Apply it like this:

```formula
g = 1 − du
where
g: the gain multiplier applied to the signal
d: the tremolo depth, from 0 (no effect) to 1 (falls to silence)
u: the LFO's unipolar value, from 0 to 1
In words: the gain moves between 1 and 1 − d and never rises above 1.
```

That keeps the peak at the original level and avoids pushing the signal past full scale.

## Key takeaways

- State which note value receives the tempo beat before deriving an LFO rate.
- Unipolar tremolo can reduce level without increasing the original peak.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
