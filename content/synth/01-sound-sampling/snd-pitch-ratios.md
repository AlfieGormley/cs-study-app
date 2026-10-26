---
id: snd-pitch-ratios
title: Pitch ratios and equal temperament
level: basic
minutes: 4
summary: Use doublings and logarithms to explain octaves and equal-tempered semitones.
sourceLesson: snd-pitch
---

A synth receives "play note 60" and has to turn it into a phase increment. Between those two is a formula you'll write in your first afternoon and use for the rest of the project. Understanding it properly also explains why pitch bends, detune and vibrato are specified in semitones and cents, not hertz.

## Pitch is a ratio, not a difference

**Frequency** is physical: cycles per second. **Pitch** is perceptual: how high or low a note sounds. For a steady periodic tone, the pitch we hear closely tracks the **fundamental frequency** (the rate at which the whole waveform repeats).

The crucial fact is that our ears judge pitch by **ratios**. Going from 110 Hz to 220 Hz sounds like the same step as going from 440 Hz to 880 Hz, even though the first is a 110 Hz difference and the second is 440 Hz. Both are a doubling, and a doubling of frequency is an **octave**.

```text
A1    A2    A3    A4    A5
55 -> 110 -> 220 -> 440 -> 880 Hz
  x2    x2    x2    x2
```

So pitch is **logarithmic** in frequency: equal steps in pitch are equal *multiplications* of frequency. This is the basis of musical pitch arithmetic.

## Exponentials and logarithms, briefly

An exponential turns a pitch offset into a frequency ratio. One octave means doubling; two octaves means doubling twice. Fractional octaves fill the spaces between those steps. A base-2 logarithm works backwards: it counts how many doublings a positive frequency ratio represents.

Adding pitch offsets combines their ratios by multiplication. Up an octave and then up another octave doubles twice, regardless of the starting note. You do not need to memorise a logarithm identity to use this idea.

The practical rule follows: **do pitch arithmetic in note space, then convert to hertz once at the end.** In note space, transposing, bending and modulating are simple additions. In hertz they're multiplications, and mixing the two up is a classic bug.

## Semitones and equal temperament

Western chromatic music commonly divides the octave into 12 **semitones**. In **twelve-tone equal temperament** (12-TET), every semitone has the same frequency ratio. Twelve of them must make an octave (×2), so each one is the number that gives 2 when 12 copies of it are multiplied together.

Each semitone up multiplies frequency by about 1.0595; twelve such steps exactly double it.

For example, the note one semitone above A4 (440 Hz) is A♯4, at about 466.16 Hz.

Equal temperament gives every key the same interval pattern. That flexibility means most intervals differ slightly from pure whole-number ratios. Simple whole-number ratios such as 3:2 (the pure ratio of a perfect fifth) don't land exactly on a 12-TET note:

| Interval | Just ratio | 12-TET ratio | Difference |
|---|---|---|---|
| Octave | 2.000 | 2.000 | 0 cents |
| Fifth | 1.500 | 1.4983 | 12-TET 1.96 cents flat |
| Major third | 1.250 | 1.2599 | 12-TET 13.69 cents sharp |

The difference column uses **cents**: hundredths of a semitone, explored in the tuning unit. 12-TET is a common default tuning; alternative tunings are a later feature.

## Pitfalls

- **Adding hertz for musical intervals.** "Up a fifth" is ×1.4983, not +220 Hz.

## Key takeaways

- An octave doubles frequency; musical intervals use ratios rather than fixed hertz differences.
- Exponentials turn octave offsets into ratios, and base-2 logarithms count doublings.
- In 12-TET, twelve identical semitone ratios multiply to two. Just intervals differ slightly.

## Further reading

- [Equal temperament — Wikipedia](https://en.wikipedia.org/wiki/Equal_temperament)
- [Cent (music) — Wikipedia](https://en.wikipedia.org/wiki/Cent_(music))
- [Notes, MIDI numbers and frequencies — UNSW](https://www.phys.unsw.edu.au/jw/notes.html)
