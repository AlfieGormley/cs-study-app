---
id: snd-cents-beating
title: Cents, tuning errors and beats
level: basic
minutes: 5
summary: Express tuning errors in cents and predict the beat rate of two close tones.
sourceLesson: snd-pitch
---

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

How small is a cent? It is often smaller than a pitch change a listener can reliably distinguish between separate tones. The just-noticeable difference depends on frequency, duration, level, timbre, training and the listener. Secondary summaries sometimes quote 3 Hz below 500 Hz or 0.6% above 1 kHz; these are rough examples, not universal thresholds. For scale, 3 Hz at 440 Hz is about 12 cents, while a 0.6% change is about 10 cents. Research finds substantial variation with test conditions, so use measured results for the particular listening task. Two tones played together are another matter: even a cent or two of mistuning can be heard as slow beating.

Cents are the natural unit for **detune**. Here's a function that finds the nearest note and how far off it is:

```python
import math

NAMES = ["C", "C#", "D", "D#", "E", "F",
         "F#", "G", "G#", "A", "A#", "B"]

def hz_to_note(f, a4=440.0):
    # Keep the fractional note for detune.
    m = 69 + 12 * math.log2(f / a4)
    n = round(m)
    # Report error from the nearest note.
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

The difference formula describes the interference envelope. A difference of a few hertz sounds like a slow level wobble. As the difference grows into tens of hertz, listeners may hear rapid beats, roughness or two distinct tones rather than a countable wobble. The perceptual boundaries depend on the tones and listener.

Because the detune is in cents, the *beat rate* grows with pitch: the same 10 cents at 880 Hz beats at about 5.1 Hz. This is why a fixed-cents detune sounds "wider" in the high register, and some synths offer a fixed-Hz detune as an alternative.

## Key takeaways

- A semitone contains 100 cents, and an octave contains 1200.
- Use a logarithm to measure an interval and an exponential to apply detune.
- Two close tones beat at their frequency difference; fixed-cents detune beats faster on higher notes.

## Further reading

- [Cent (music) — Wikipedia](https://en.wikipedia.org/wiki/Cent_(music))
- [Frequency-discrimination study — Micheyl, Xiao & Oxenham](https://pubmed.ncbi.nlm.nih.gov/22841571/)
- [Beats and their perception — UNSW Physclips](https://www.animations.physics.unsw.edu.au/jw/beats.htm)
- [Beat (acoustics) — Wikipedia](https://en.wikipedia.org/wiki/Beat_(acoustics))
