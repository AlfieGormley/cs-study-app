---
id: snd-pitch
title: Pitch and tuning
level: basic
minutes: 13
summary: Octaves, semitones and equal temperament; MIDI note numbers and f = 440·2^((n−69)/12); cents and detuning; why pitch is logarithmic; and the difference between pitch and timbre.
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

So pitch is **logarithmic** in frequency: equal steps in pitch are equal *multiplications* of frequency. This is the single most important idea in the lesson.

## Exponentials and logarithms, briefly

Two identities do almost all the work:

- **2^(a+b) = 2^a · 2^b.** Adding in the exponent multiplies the result. Transposing up an octave (+1 in the exponent) doubles the frequency, whatever note you started on.
- **log2(x) is the inverse of 2^x.** It answers "how many doublings make x?". log2(8) = 3, log2(1.5) ≈ 0.585. Most languages offer `log2`; otherwise use log2(x) = ln(x)/ln(2).

The practical rule follows: **do pitch arithmetic in note space, then convert to hertz once at the end.** In note space, transposing, bending and modulating are simple additions. In hertz they're multiplications, and mixing the two up is a classic bug.

## Semitones and equal temperament

Western music divides the octave into 12 **semitones**. In **twelve-tone equal temperament** (12-TET), every semitone has the same frequency ratio. Twelve of them must make an octave (×2), so each one is:

```text
semitone ratio = 2^(1/12) ≈ 1.059463
```

That irrational ratio is the price of a tuning where every key is equally in tune. Simple whole-number ratios such as 3:2 (a "perfect" fifth) don't land exactly on a 12-TET note:

| Interval | Just ratio | 12-TET ratio | Difference |
|---|---|---|---|
| Octave | 2.000 | 2.000 | 0 cents |
| Fifth | 1.500 | 1.4983 | 12-TET 1.96 cents flat |
| Major third | 1.250 | 1.2599 | 12-TET 13.69 cents sharp |

The difference column uses **cents**, defined below. Almost all synths default to 12-TET; alternative tunings are a later feature.

## MIDI note numbers

MIDI identifies notes with a number from **0 to 127**. Note **60 is middle C**, and **69 is the A above it**, which is tuned to **440 Hz** by convention. Each step of 1 is one semitone. So:

```text
f = 440 · 2^((n − 69) / 12)
n = 69 + 12 · log2(f / 440)
```

These are the standard conversion formulas (the Wikipedia article on the MIDI Tuning Standard gives both). Reading the first: n − 69 is semitones away from A4; dividing by 12 gives octaves; 2 to that power is the frequency ratio.

```python
def midi_to_hz(n, a4=440.0):
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
> In scientific pitch notation middle C is **C4**, so note 60 = C4 and 69 = A4. Some software and instruments label note 60 as C3 instead: Ableton Live, for example, calls middle C "C3". The number on the wire is always 60, so think in note numbers and check how each piece of gear displays them.

Keep the 440 as a parameter (`a4` above). A "master tune" control is just a different reference.

## Cents

A **cent** is 1/100 of a 12-TET semitone, so there are 1200 cents per octave. The distance between two frequencies in cents is:

```text
cents = 1200 · log2(f2 / f1)
```

And to shift a frequency by c cents, multiply by 2^(c/1200).

How small is a cent? Below what most people can hear as a pitch change. Published figures for the just-noticeable difference vary: one commonly cited summary gives about 3 Hz for sine tones below 500 Hz (roughly 12 cents at 440 Hz, and far more at bass frequencies) and about 0.6%, roughly 10 cents, above 1 kHz. Some sources quote 5–6 cents for attentive listeners. It varies with frequency, level, timbre, context and the listener, so treat any single number as a rough guide. Two tones played together are another matter: even a cent or two of mistuning can be heard as slow beating.

Cents are the natural unit for **detune**. Here's a function that finds the nearest note and how far off it is:

```python
import math

NAMES = ["C", "C#", "D", "D#", "E", "F",
         "F#", "G", "G#", "A", "A#", "B"]

def hz_to_note(f, a4=440.0):
    m = 69 + 12 * math.log2(f / a4)
    n = round(m)
    cents = 100 * (m - n)
    name = NAMES[n % 12] + str(n // 12 - 1)
    return n, name, cents

for f in (261.63, 450.0, 430.0, 100.0):
    n, name, c = hz_to_note(f)
    tag = f"{c:+.1f}c"
    print(f"{f:.2f} ->", n, name, tag)
```

```text
261.63 -> 60 C4 +0.0c
450.00 -> 69 A4 +38.9c
430.00 -> 69 A4 -39.8c
100.00 -> 43 G2 +35.0c
```

The `n // 12 − 1` gives the octave number in scientific pitch notation, because note 0 is C−1.

## Detuning and beats

Play two oscillators at nearly the same frequency and you hear the level wobble. That's **beating**: the two sines drift in and out of phase, reinforcing then cancelling. The beat rate is the difference in frequency, |f1 − f2|.

Detune one 440 Hz oscillator by +10 cents:

```text
f2 = 440 · 2^(10/1200) ≈ 442.55 Hz
beat rate ≈ 2.55 Hz
```

Because the detune is in cents, the *beat rate* grows with pitch: the same 10 cents at 880 Hz beats at about 5.1 Hz. This is why a fixed-cents detune sounds "wider" in the high register, and some synths offer a fixed-Hz detune as an alternative.

## Linear vs exponential modulation

Suppose an LFO adds vibrato. Two ways to do it:

1. **Linear (in Hz):** f = 440 + 10·lfo. At 440 Hz, ±10 Hz is about ±39 cents. At 110 Hz the same ±10 Hz swings about +151 and −165 cents, a much wider wobble.
2. **Exponential (in pitch):** f = 440 · 2^(depth·lfo/1200), with depth in cents. The vibrato sounds equally deep on every note.

Option 2 is what players expect for vibrato and pitch bend. MIDI pitch bend, for example, is normally interpreted as a number of semitones (the bend range), added in note space.

Analogue synths face the same problem in hardware. The common **1 volt per octave** standard, popularised by Moog, makes control voltage linear in pitch: each extra volt doubles the oscillator frequency, using an exponential converter inside the oscillator.

## Pitch vs timbre

Play a sine and a sawtooth at 220 Hz. They have the **same pitch** but sound completely different. The difference is **timbre**, often loosely called "tone colour".

A sawtooth at 220 Hz contains sine components at 220, 440, 660, 880 Hz and so on: the **harmonic series**, every whole-number multiple of the fundamental, with amplitudes falling as 1/k. A sine has only the 220 Hz component. Because all the extra components are exact multiples, the waveform still repeats every 1/220 s, and the ear still hears 220 Hz.

The harmonic series is also where just ratios come from: harmonics 2, 3, 4, 5 give an octave, a fifth above that, another octave, and a major third. The 5th harmonic of 110 Hz is 550 Hz, about 14 cents below the 12-TET C♯5 (554.37 Hz).

Timbre also depends on how the sound changes over time: the attack, how harmonics fade, noise. Subtractive synthesis works by starting with a harmonically rich wave and filtering harmonics away, changing timbre while leaving pitch alone. That's the next module.

> [!note] The missing fundamental
> Pitch perception isn't just "find the lowest component". If you remove the 220 Hz component from a sawtooth and keep 440, 660, 880 Hz and so on, most listeners still hear a pitch of 220 Hz, because the harmonics are spaced 220 Hz apart. This is why small speakers can suggest bass notes they can't reproduce.

## Pitfalls

- **Adding hertz for musical intervals.** "Up a fifth" is ×1.4983, not +220 Hz.
- **Integer division.** In C-family languages, `(n − 69) / 12` with integers truncates to whole octaves. Use floating point.
- **Assuming octave labels.** Use note numbers between systems.
- **Converting too early.** Keep pitch as a float note number (including bend, detune and modulation in semitones), then convert to hertz, then to a phase increment.

## Key takeaways
- Pitch is perceived logarithmically: an octave is ×2 in frequency, a 12-TET semitone ×2^(1/12) ≈ 1.0595.
- f = 440·2^((n−69)/12); n = 69 + 12·log2(f/440). Note 60 is middle C, 69 is A 440 Hz.
- Cents = 1200·log2(f2/f1); 100 cents per semitone. Detune in cents; beat rate = |f1 − f2|.
- Do pitch maths in note space, then convert once to hertz and then to a phase increment.
- Same pitch, different harmonic content = different timbre.

## Further reading
- [MIDI Tuning Standard — Wikipedia](https://en.wikipedia.org/wiki/MIDI_tuning_standard)
- [MIDI 1.0 core specifications — MIDI Association](https://midi.org/midi-1-0-core-specifications)
- [Equal temperament — Wikipedia](https://en.wikipedia.org/wiki/Equal_temperament)
- [Cent (music) — Wikipedia](https://en.wikipedia.org/wiki/Cent_(music))
- [Just-noticeable difference — Wikipedia](https://en.wikipedia.org/wiki/Just-noticeable_difference)
- [Piano key frequencies — Wikipedia](https://en.wikipedia.org/wiki/Piano_key_frequencies)
- [Beat (acoustics) — Wikipedia](https://en.wikipedia.org/wiki/Beat_(acoustics))
- [CV/gate — Wikipedia](https://en.wikipedia.org/wiki/CV/gate)
- [Timbre — Wikipedia](https://en.wikipedia.org/wiki/Timbre)
