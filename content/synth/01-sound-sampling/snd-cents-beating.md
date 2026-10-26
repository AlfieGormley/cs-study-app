---
id: snd-cents-beating
title: Cents, tuning errors and beats
level: basic
minutes: 4
summary: Express tuning errors in cents and predict the beat rate of two close tones.
sourceLesson: snd-pitch
---

## Cents

A **cent** is 1/100 of a 12-TET semitone, so there are 1200 cents per octave. To measure how far apart two frequencies are in pitch, count the octaves between them and multiply by 1200:

```formula reference
c = 1200 log_2(f_2 / f_1)
where
c: the interval from f_1 up to f_2, in cents (negative if f_2 is lower)
f_1: the reference frequency, in hertz (Hz); here 440 Hz
f_2: the other frequency, in hertz (Hz); here 445 Hz
log_2: the base-2 logarithm, which counts octaves in a frequency ratio
cents: hundredths of a semitone; 1200 make an octave
In words: compare the frequency ratio to count pitch distance in cents. A higher second frequency gives a positive interval; a lower one gives a negative interval.
```

To apply a cents detune, multiply by the ratio for that interval. The reference conversion is:

```formula reference
f_2 = f_1 × 2^(c / 1200)
where
f_2: the shifted frequency, in hertz (Hz)
f_1: the starting frequency, in hertz (Hz)
c: the shift in cents (positive is sharp, negative is flat)
In words: A fixed cents offset multiplies every starting frequency by the same ratio: positive cents sharpen it and negative cents flatten it.
```

How small is a cent? It is often smaller than a pitch change a listener can reliably distinguish between separate tones. The just-noticeable difference depends on frequency, duration, level, timbre, training and the listener. Research finds substantial variation with test conditions, so use measured results for the particular listening task. Two tones played together are another matter: even a cent or two of mistuning can be heard as slow beating.

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

Play two oscillators at nearly the same frequency and you hear the level wobble. That's **beating**: the two sines drift in and out of phase, reinforcing then cancelling. The wobble happens once for every cycle one oscillator gains on the other, so its rate is the difference in frequency. For example, detuning one 440 Hz oscillator by +10 cents produces about 442.55 Hz. The pair beats about 2.55 times per second.

The frequency difference describes the interference envelope. A difference of a few hertz sounds like a slow level wobble. As the difference grows into tens of hertz, listeners may hear rapid beats, roughness or two distinct tones rather than a countable wobble. The perceptual boundaries depend on the tones and listener.

Because the detune is in cents, the *beat rate* grows with pitch: the same 10 cents at 880 Hz beats at about 5.1 Hz. This is why a fixed-cents detune sounds "wider" in the high register, and some synths offer a fixed-Hz detune as an alternative.

## Key takeaways

- A semitone contains 100 cents, and an octave contains 1200.
- Use a logarithm to measure an interval and an exponential to apply detune.
- Two close tones beat at their frequency difference; fixed-cents detune beats faster on higher notes.

## Further reading

- [Cent (music) — Wikipedia](https://en.wikipedia.org/wiki/Cent_(music))
- [Pitch discrimination and harmonicity — Micheyl, Ryan & Oxenham](https://pmc.ncbi.nlm.nih.gov/articles/PMC3356318/)
- [Beats and their perception — UNSW Physclips](https://www.animations.physics.unsw.edu.au/jw/beats.htm)
- [Beat (acoustics) — Wikipedia](https://en.wikipedia.org/wiki/Beat_(acoustics))
