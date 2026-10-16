---
id: midi-messages-bend-frequency
title: Map pitch bend into a pitch offset
level: intermediate
minutes: 3
sourceLesson: midi-messages
summary: Make the bend mapping explicit, keep centre exact, and account for the one-step asymmetry of the raw value range.
---

## Choosing the pitch-bend range
How far is "full bend"? The receiver decides, or it is set via RPN 0. A ±2 semitone range is a common default. To turn the raw value into a pitch offset, measure how far it is from centre as a fraction of half the range, then scale by the bend range:

```formula
s = ((v − 8192) / 8192)r
s = ((12288 − 8192) / 8192) × 2
s = (4096 / 8192) × 2 = 1
where
s: the pitch offset in semitones; negative bends down, positive bends up
v: the received 14-bit bend value, 0 to 16,383
8192: the centre value, meaning no bend
r: the bend range in semitones, set by the receiver or by RPN 0; 2 here (±2 semitones)
In words: a value 4,096 counts above centre bends up by half the configured range with this mapping, here one semitone.
```

To apply the offset, scale the note's frequency by the same semitone factor as the key-to-frequency formula in the note-frequency unit:

```formula
f_bent = f 2^{s / 12}
f_bent = 440 Hz × 2^{1 / 12}
f_bent ≈ 466.16 Hz
where
f_bent: the frequency actually played with the bend applied, in hertz (Hz)
f: the frequency of the held note without bend, in hertz; here 440 Hz (key 69)
s: the bend offset in semitones from the formula above; here +1
Hz: hertz, cycles per second
2^{…}: 2 raised to the power in braces; a power of 1/12 is one semitone up
≈: approximately equal to (rounded)
In words: bending A 440 up one semitone gives the B♭ just above it, about 466 Hz.
```

Mapping the raw value to semitones in Python:

```python
def bend_semitones(value, rng=2):
    # rng = bend range in semitones (RPN 0)
    # Keep 8192 exactly at the zero offset.
    return (value - 8192) / 8192 * rng

# Output: raw value then semitone offset.
for v in (0, 8192, 12288, 16383):
    print(v, round(bend_semitones(v), 4))
```

```output
0 -2.0
8192 0.0
12288 1.0
16383 1.9998
```

The range is asymmetric by one step (8,192 values below centre, 8,191 above). This is an implementation mapping, not a MIDI-mandated bend law. An implementation can instead divide the upper half by 8,191 to make the maximum reach exactly the configured positive range; keep the centre exactly zero and document the choice.

> [!warning] Reset bend to centre, not zero
> A raw value of 0 is *full downward* bend. Initialise and reset pitch bend to 8,192. The spec's "Reset All Controllers" (CC 121) likewise returns pitch bend to centre.

## Key takeaways
- Make the bend mapping explicit, keep centre exact, and account for the one-step asymmetry of the raw value range.

## Further reading
- [MIDI 1.0 Control Change Messages — MIDI Association](https://midi.org/midi-1-0-control-change-messages)
- [Summary of MIDI 1.0 Messages — MIDI Association](https://midi.org/summary-of-midi-1-0-messages)
- [MIDI 1.0 Detailed Specification 4.2.1 (archived copy at CCRMA)](https://ccrma.stanford.edu/~esteban/teaching/McGill_MUMT306/M1_v4-2-1_MIDI_1-0_Detailed_Specification_96-1-4.pdf)
- [Details about MIDI 2.0, MIDI-CI, Profiles and Property Exchange — MIDI Association](https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023)
- [MIDI 2.0 — Wikipedia](https://en.wikipedia.org/wiki/MIDI_2.0)
