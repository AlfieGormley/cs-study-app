---
id: snd-pitch-ratios
title: Pitch ratios and equal temperament
level: basic
minutes: 5
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

Two identities do almost all the work. The first says that adding in an exponent (the small raised number, "the power") multiplies the result:

```formula
2^(a + b) = 2^a × 2^b
2^(1 + 0.5) = 2 × 1.414 ≈ 2.83
where
2^a: 2 raised to the power a: for a non-negative whole number, a copies of 2 multiplied together; fractional powers use roots and negative powers use reciprocals (e.g. 2^0.5 ≈ 1.414 and 2^−1 = 0.5)
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

Western chromatic music commonly divides the octave into 12 **semitones**. In **twelve-tone equal temperament** (12-TET), every semitone has the same frequency ratio. Twelve of them must make an octave (×2), so each one is the number that gives 2 when 12 copies of it are multiplied together:

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
