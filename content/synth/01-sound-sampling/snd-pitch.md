---
id: snd-pitch
title: Pitch and tuning
level: basic
minutes: 17
summary: Octaves, semitones and equal temperament; converting MIDI note numbers to hertz; cents and detuning; why pitch is logarithmic; and the difference between pitch and timbre.
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

Two identities do almost all the work. The first says that adding in an exponent (the small raised number, "the power") multiplies the result:

```formula
2^(a + b) = 2^a × 2^b
2^(1 + 0.5) = 2 × 1.414 ≈ 2.83
where
2^a: 2 raised to the power a: a copies of 2 multiplied together (fractional and negative powers are allowed, e.g. 2^0.5 ≈ 1.414 and 2^−1 = 0.5)
a: any number, here an amount of octaves
b: any other number, here another amount of octaves
≈: approximately equal to (rounded)
In words: adding exponents multiplies the results. Transposing up an octave (+1 in the exponent) doubles the frequency, whatever note you started on.
```

The second undoes the first. The base-2 logarithm answers "how many doublings make x?":

```formula
2^y = x
y = log_2(x)
log_2(8) = 3
log_2(1.5) ≈ 0.585
log_2(x) = ln(x) / ln(2)
where
log_2: the base-2 logarithm, the inverse of "2 to the power of"
x: any positive number, typically a frequency ratio
y: the number of doublings (octaves) that make x
ln: the natural logarithm (base e ≈ 2.718), which every maths library has; dividing by ln(2) converts it to base 2
≈: approximately equal to (rounded)
In words: if 2 to the power y gives x, then y is the base-2 logarithm of x, so log_2 counts doublings. 8 is three doublings of 1, and a ratio of 1.5 is a little over half a doubling.
```

Most languages offer `log2`; otherwise use the last line, which works because any logarithm divided by the same logarithm of 2 gives the base-2 version. Logarithms are defined only for positive numbers, which is fine here: frequencies and their ratios are always positive.

The practical rule follows: **do pitch arithmetic in note space, then convert to hertz once at the end.** In note space, transposing, bending and modulating are simple additions. In hertz they're multiplications, and mixing the two up is a classic bug.

## Semitones and equal temperament

Western music divides the octave into 12 **semitones**. In **twelve-tone equal temperament** (12-TET), every semitone has the same frequency ratio. Twelve of them must make an octave (×2), so each one is the number that gives 2 when 12 copies of it are multiplied together:

```formula
r = 2^(1/12)
r ≈ 1.059463
r^12 = 2
where
r: the frequency ratio of one 12-TET semitone (no unit: it's a ratio)
2^(1/12): 2 to the power one-twelfth, the twelfth root of 2
≈: approximately equal to (rounded)
In words: each semitone up multiplies the frequency by about 1.0595, and twelve of those steps exactly double it.
```

For example, the note one semitone above A4 (440 Hz) is A♯4, at 440 × 1.059463 ≈ 466.16 Hz.

That irrational ratio is the price of a tuning where every key is equally in tune. Simple whole-number ratios such as 3:2 (the pure ratio of a perfect fifth) don't land exactly on a 12-TET note:

| Interval | Just ratio | 12-TET ratio | Difference |
|---|---|---|---|
| Octave | 2.000 | 2.000 | 0 cents |
| Fifth | 1.500 | 1.4983 | 12-TET 1.96 cents flat |
| Major third | 1.250 | 1.2599 | 12-TET 13.69 cents sharp |

The difference column uses **cents**, defined below. Almost all synths default to 12-TET; alternative tunings are a later feature.

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

A **cent** is 1/100 of a 12-TET semitone, so there are 1200 cents per octave. To measure how far apart two frequencies are in pitch, count the octaves between them and multiply by 1200:

```formula
c = 1200 × log_2(f_2 / f_1)
c = 1200 × log_2(445 / 440)
c ≈ 19.6 cents
where
c: the interval from f_1 up to f_2, in cents (negative if f_2 is lower)
f_1: the reference frequency, in hertz (Hz); here 440 Hz
f_2: the other frequency, in hertz (Hz); here 445 Hz
log_2: the base-2 logarithm, which counts octaves in a frequency ratio
cents: hundredths of a semitone; 1200 make an octave
≈: approximately equal to (rounded)
In words: 445 Hz is about 19.6 cents (a fifth of a semitone) above 440 Hz.
```

To shift a frequency by a number of cents, undo the logarithm:

```formula
f_2 = f_1 × 2^(c / 1200)
where
f_2: the shifted frequency, in hertz (Hz)
f_1: the starting frequency, in hertz (Hz)
c: the shift in cents (positive is sharp, negative is flat)
In words: a shift of c cents multiplies the frequency by 2 to the power c/1200, the same ratio on every note.
```

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

Play two oscillators at nearly the same frequency and you hear the level wobble. That's **beating**: the two sines drift in and out of phase, reinforcing then cancelling. The wobble happens once for every cycle one oscillator gains on the other, so its rate is the difference in frequency. Detune one 440 Hz oscillator by +10 cents:

```formula
f_2 = 440 × 2^(10 / 1200) ≈ 442.55 Hz
f_beat = |f_1 − f_2|
f_beat = |440 − 442.55| ≈ 2.55 Hz
where
f_1: the first oscillator's frequency, in hertz (Hz); here 440 Hz
f_2: the detuned oscillator's frequency, in hertz (Hz)
f_beat: the beat rate, how many times per second the level swells and dips, in hertz (Hz)
|…|: absolute value: the size of the difference, ignoring its sign
Hz: hertz, cycles per second
≈: approximately equal to (rounded)
In words: the level wobbles at the difference between the two frequencies, here about 2.55 times a second.
```

This holds for two tones close in frequency (within a few hertz to a few tens of hertz); tones far apart don't produce an audible wobble.

Because the detune is in cents, the *beat rate* grows with pitch: the same 10 cents at 880 Hz beats at about 5.1 Hz. This is why a fixed-cents detune sounds "wider" in the high register, and some synths offer a fixed-Hz detune as an alternative.

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

Analogue synths face the same problem in hardware. The common **1 volt per octave** standard, popularised by Moog, makes control voltage linear in pitch: each extra volt doubles the oscillator frequency, using an exponential converter inside the oscillator.

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

## Pitch vs timbre

Play a sine and a sawtooth at 220 Hz. They have the **same pitch** but sound completely different. The difference is **timbre**, often loosely called "tone colour".

A sawtooth at 220 Hz contains sine components at 220, 440, 660, 880 Hz and so on: the **harmonic series**, every whole-number multiple of the fundamental. In an ideal sawtooth their amplitudes fall off steadily:

```formula
f_k = k × f_0
a_k = 1 / k
where
f_k: the frequency of harmonic number k, in hertz (Hz)
k: the harmonic number, a whole number 1, 2, 3, …; k = 1 is the fundamental
f_0: the fundamental frequency, in hertz (Hz); here 220 Hz
a_k: the amplitude of harmonic k, relative to the fundamental (no unit)
In words: harmonic k sits at k times the fundamental and, in a sawtooth, has 1/k of its amplitude: the 3rd harmonic of 220 Hz is at 660 Hz with a third of the amplitude.
```

A sine has only the 220 Hz component. Because all the extra components are exact multiples, the waveform still repeats every 1/220 s, and the ear still hears 220 Hz.

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
- Pitch is perceived logarithmically: an octave is ×2 in frequency, a 12-TET semitone about ×1.0595 (the twelfth root of 2).
- Note number to frequency: 440 Hz times 2 to the power (note − 69)/12. Note 60 is middle C, 69 is A 440 Hz.
- An interval in cents is 1200 times the base-2 logarithm of the frequency ratio; 100 cents per semitone. Detune in cents; two close tones beat at the difference of their frequencies.
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
