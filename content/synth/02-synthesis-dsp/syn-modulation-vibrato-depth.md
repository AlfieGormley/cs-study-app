---
id: syn-modulation-vibrato-depth
title: Vibrato in cents and semitones
level: intermediate
minutes: 3
summary: Vibrato in cents and semitones.
sourceLesson: syn-modulation
---

## Vibrato and tremolo

**Vibrato** is periodic pitch variation; **tremolo** is periodic amplitude variation. (Some instruments and effects use the names loosely; synths use them precisely.)

**Pitch depth belongs in cents or semitones**, because pitch is heard logarithmically. Add the modulation in semitones (or cents), then convert:

```formula
f = f_note 2^{s/12}
f = f_note 2^{c/1200}
f = 440 Hz × 2^{50/1200} ≈ 452.89 Hz
where
f: the modulated frequency, in hertz (Hz)
f_note: the note's unmodulated frequency, in Hz
s: the pitch offset in semitones (12 to an octave), positive or negative; for vibrato, the LFO value times the depth in semitones
c: the same offset in cents (100 to a semitone, 1200 to an octave)
2^{x}: 2 raised to the power x: +12 semitones (+1200 cents) doubles f, −12 halves it
Hz: hertz
≈: approximately equal to
In words: add modulation in musical units, then convert by doubling the frequency for every 12 semitones; 50 cents above 440 Hz is about 452.89 Hz.
```

| Vibrato depth | 440 Hz swings between |
|---|---|
| ±50 cents | 427.47 – 452.89 Hz |
| ±100 cents | 415.30 – 466.16 Hz |

For vibrato intended to have the same musical interval on every note, a fixed depth in hertz is unsuitable: ±10 Hz is a wide vibrato on a bass note and barely noticeable on a high one.

## Key takeaways

- Vibrato changes pitch; tremolo changes amplitude.
- Cents and semitones preserve musical width across the keyboard.
- A fixed hertz deviation has a different purpose in linear FM.

## Further reading

- [Notes, octaves and frequency — UNSW Acoustics](https://newt.phys.unsw.edu.au/jw/notes.html)
- [Sinusoidal FM and PM — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Sinusoidal_Frequency_Modulation_FM.html)
