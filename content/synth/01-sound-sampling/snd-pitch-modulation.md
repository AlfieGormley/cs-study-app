---
id: snd-pitch-modulation
title: Vibrato and pitch-space arithmetic
level: basic
minutes: 3
summary: Compare fixed-hertz and fixed-cents vibrato and combine bend, detune and modulation before conversion.
sourceLesson: snd-pitch
---

## Linear vs exponential modulation

Suppose an LFO adds vibrato. Two ways to do it:

1. **Linear (in Hz):** add a fixed number of hertz.
2. **Exponential (in pitch):** multiply by a fixed ratio, set in cents.

```formula reference
f_lin = f_0 + D × L
f_exp = f_0 × 2^(d × L / 1200)
where
f_lin: the frequency with linear (hertz) vibrato, in hertz (Hz)
f_exp: the frequency with exponential (pitch) vibrato, in hertz (Hz)
f_0: the note's unmodulated frequency, in hertz (Hz)
L: the LFO's current output, swinging between −1 and +1
D: the linear vibrato depth, in hertz (Hz); for example 10 Hz
d: the exponential vibrato depth, in cents; for example 39 cents
In words: linear vibrato swings the frequency by the same number of hertz on every note; exponential vibrato swings it by the same musical interval on every note.
```

A fixed 10 Hz swing is a much larger fraction of a 110 Hz bass note than of a 440 Hz note. Its musical interval is therefore wider in the bass. Specifying a fixed cents depth instead gives the same pitch interval in each register.

Option 2 is what players expect for vibrato and pitch bend. MIDI pitch bend, for example, is normally interpreted as a number of semitones (the bend range), added in note space.

Analogue synths face the same problem in hardware. The common **1 volt per octave** standard, used by Moog instruments, makes control voltage linear in pitch: each extra volt doubles the oscillator frequency, using an exponential converter inside the oscillator.

For example, two extra volts request two octaves: a 110 Hz oscillator would ideally become 440 Hz. A semitone needs one twelfth of a volt. Real oscillators follow this law only over a limited range, which is why analogue synths need calibrating.

## Pitfalls

- **Converting too early.** Keep pitch as a float note number (including bend, detune and modulation in semitones), then convert to hertz, then to a phase increment.

## Key takeaways

- Fixed-hertz modulation changes its musical depth across the keyboard.
- Fixed-cents modulation applies the same interval on every note.
- Add bend, detune and modulation in note space, then convert to frequency and phase increment.

## Further reading

- [MIDI Tuning Standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [CV/gate — Wikipedia](https://en.wikipedia.org/wiki/CV/gate)
