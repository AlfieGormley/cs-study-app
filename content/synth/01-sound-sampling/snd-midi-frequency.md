---
id: snd-midi-frequency
title: Convert MIDI notes to frequency
level: basic
minutes: 4
summary: Turn note numbers into hertz, invert the conversion and avoid integer-division and octave-label bugs.
sourceLesson: snd-pitch
---

## MIDI note numbers

MIDI identifies notes with a number from **0 to 127**. Note **60 is middle C**, and **69 is the A above it**, which is tuned to **440 Hz** by convention. Each step of 1 is one semitone. Your synth needs to turn a note number into a frequency, and the standard conversion (the Wikipedia article on the MIDI Tuning Standard gives it) is:

```formula
f = 440 × 2^((n − 69) / 12)
f = 440 × 2^((60 − 69) / 12)
f = 440 × 2^(−0.75)
f ≈ 261.63 Hz
where
f: the frequency to play, in hertz (Hz)
n: the MIDI note number, 0 to 127 (or a fractional value once bends and detune are added); here 60, middle C
440: the reference frequency of note 69 (A4), in hertz
69: the note number of A4, the reference note
12: semitones per octave
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: count semitones away from A4 (n − 69), divide by 12 to get octaves, raise 2 to that power to get a frequency ratio, and multiply by 440 Hz.
```

Going the other way, a tuner or a pitch detector turns a frequency back into a (usually fractional) note number:

```formula
n = 69 + 12 × log_2(f / 440)
n = 69 + 12 × log_2(880 / 440)
n = 69 + 12 × 1 = 81
where
n: the note number, fractional in general; the nearest whole number is the nearest note
f: the measured frequency, in hertz (Hz); here 880 Hz
log_2: the base-2 logarithm, which counts doublings
440: the reference frequency of A4, in hertz
69: the note number of A4
12: semitones per octave
In words: count how many octaves the frequency is above or below 440 Hz, turn that into semitones (× 12), and add it to 69. 880 Hz is exactly one octave up, note 81.
```

Both formulas assume 12-TET and A4 = 440 Hz; another tuning system or reference pitch changes the constants.

```python
def midi_to_hz(n, a4=440.0):
    # Semitone offset becomes a ratio.
    return a4 * 2 ** ((n - 69) / 12)

for n in (0, 21, 57, 60, 69, 81, 108, 127):
    print(f"{n:>3} {midi_to_hz(n):9.2f} Hz")
```

```text
  0      8.18 Hz
 21     27.50 Hz
 57    220.00 Hz
 60    261.63 Hz
 69    440.00 Hz
 81    880.00 Hz
108   4186.01 Hz
127  12543.85 Hz
```

Notes 21 to 108 are the 88 keys of a piano (A0 to C8). Note 0, at about 8.2 Hz, is below hearing; you'd hear it only through its harmonics.

> [!warning] Octave labels vary, numbers don't
> In scientific pitch notation middle C is **C4**, so note 60 = C4 and 69 = A4. Some software and instruments label note 60 as C3 instead: Ableton Live’s manual gives its full MIDI range as C−2 to G8, which places note 60 at C3. The number on the wire is always 60, so think in note numbers and check how each piece of gear displays them.

Keep the 440 as a parameter (`a4` above). A "master tune" control is just a different reference.

## Pitfalls

- **Integer division.** In C-family languages, `(n − 69) / 12` with integers truncates to whole octaves. Use floating point.
- **Assuming octave labels.** Use note numbers between systems.

## Key takeaways

- The conventional 12-TET reference is note 69 at 440 Hz, with one semitone per note-number step.
- Use floating-point division in the exponent and keep the reference pitch configurable.
- Note 60 is middle C; displayed octave names vary between products.

## Further reading

- [MIDI Tuning Standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [MIDI 1.0 core specifications — MIDI Association](https://midi.org/midi-1-0-core-specifications)
- [Piano key frequencies — Wikipedia](https://en.wikipedia.org/wiki/Piano_key_frequencies)
- [Sampler key range — Ableton Live 12 manual](https://www.ableton.com/en/live-manual/12/live-instrument-reference/)
- [Tuning reference and note mapping — MIDI Association](https://midi.org/microtuning-and-alternative-intonation-systems)
