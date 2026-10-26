---
id: ds-sines-phase
title: Sines, cycles and phase
level: basic
minutes: 3
summary: Describe a sampled sinusoid using amplitude, frequency and phase.
---

A **sinusoid** is a smooth repeating wave described by sine or cosine. It is useful as a controlled test signal: its amplitude, frequency and timing can be varied separately. **Amplitude** here means the maximum magnitude of the ideal wave relative to its centre. **Frequency** counts cycles per second, measured in **hertz (Hz)**. A 2 Hz wave repeats twice per second.

**Phase** tells us where in the cycle a wave starts. An angle in **radians** measures arc length divided by radius. A full turn is twice pi radians; pi is about 3.14159. A quarter turn is half pi radians. At zero starting phase, sine starts at zero and rises; cosine starts at its positive maximum.

## A wave sampled at regular instants

Imagine sampling one complete cycle at four equally spaced positions. A unit-amplitude sine starting at zero phase gives approximately `[0, 1, 0, -1]`. The next sample begins the next cycle.

Changing amplitude scales the height without changing the repetition rate. Changing frequency changes how far through a cycle each new sample advances. Changing starting phase chooses a different starting point without changing that advance. A quarter-turn starting phase makes this sine start at its positive maximum.

A finite set of samples need not hit the ideal wave’s maximum. Its largest recorded sample can therefore be smaller than the stated amplitude. That alone does not show that the generator used the wrong amplitude.

This reference expression describes the same three controls for a sampled sine:

```formula reference
x[n] = A sin(2πfn / F_s + φ)
0 ≤ n ≤ N − 1
where
x: sampled signal, in the same units as A
n: integer sample index, starting at zero
A: non-negative sinusoid amplitude, in the signal’s units
sin: sine function, taking an angle in radians and returning a unitless value between −1 and 1
π: pi, about 3.14159
f: sinusoid frequency, in hertz (Hz)
F_s: sample rate, in samples per second
φ: starting phase, in radians
N: positive number of samples
Hz: hertz, one cycle per second
In words: Amplitude controls wave height, frequency controls progress through each cycle, and starting phase chooses the initial position. At a fixed sample rate, increasing frequency advances farther through the cycle between samples.
```

> [!analogy] Real-world analogy: A hand on a clock
> Picture a hand turning at a steady rate.
>
> **How it maps:** Its turning rate represents frequency and its starting direction represents phase. The vertical height of its tip behaves like a sine wave.
>
> **Where it stops:** The rotating hand is a geometric aid; a measured signal does not need to be a physical rotating object.

## Frequency per sample

**Normalised frequency** must name its convention. Here it means cycles per sample; some other texts instead use radians per sample or a fraction of the Nyquist frequency. Never transfer a bare number between these conventions.

One cycle every four sample intervals means one quarter of a cycle per sample. At a fixed frequency in hertz, sampling more often reduces the advance between samples. At a fixed cycles-per-sample frequency, interpreting the same sequence at a higher sample rate makes it repeat faster in physical time.

Always keep the sample rate with a test signal. A waveform’s appearance alone cannot establish its frequency in hertz, and sampling can make different continuous waves look identical, as the next lesson explains.

## Key takeaways
- Amplitude controls height, frequency controls repetition and phase controls the cycle’s starting point.
- Recorded samples can miss the ideal wave’s maximum.
- Always label a normalised-frequency convention.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH8.PDF)
