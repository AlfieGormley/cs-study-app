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

```formula
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

With D of 10 Hz, a 440 Hz note swings about ±39 cents. At 110 Hz the same ±10 Hz swings about +151 and −165 cents, a much wider wobble. With exponential vibrato, d sets the depth in cents, and it sounds equally deep on every note.

Option 2 is what players expect for vibrato and pitch bend. MIDI pitch bend, for example, is normally interpreted as a number of semitones (the bend range), added in note space.

Analogue synths face the same problem in hardware. The common **1 volt per octave** standard, used by Moog instruments, makes control voltage linear in pitch: each extra volt doubles the oscillator frequency, using an exponential converter inside the oscillator.

```formula
f = f_0 × 2^V
f = 110 × 2^2 = 440 Hz
where
f: the oscillator frequency, in hertz (Hz)
f_0: the frequency the oscillator plays at 0 V, in hertz (Hz); here 110 Hz
V: the control voltage, in volts (V); here 2 V. Strictly it's V divided by 1 volt, so the exponent has no unit
Hz: hertz, cycles per second
In words: every extra volt of control voltage raises the pitch one octave, and 1/12 V raises it one semitone.
```

Real oscillators only follow this law over a limited range, which is why analogue synths need calibrating.

## Pitfalls

- **Converting too early.** Keep pitch as a float note number (including bend, detune and modulation in semitones), then convert to hertz, then to a phase increment.

## Key takeaways

- Fixed-hertz modulation changes its musical depth across the keyboard.
- Fixed-cents modulation applies the same interval on every note.
- Add bend, detune and modulation in note space, then convert to frequency and phase increment.

## Further reading

- [MIDI Tuning Standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [CV/gate — Wikipedia](https://en.wikipedia.org/wiki/CV/gate)
