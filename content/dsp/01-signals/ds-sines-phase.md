---
id: ds-sines-phase
title: Sines, cycles and phase
level: basic
minutes: 5
summary: Describe a sampled sinusoid using amplitude, frequency and phase.
---

A **sinusoid** is a smooth repeating wave described by sine or cosine. It is useful as a controlled test signal: its amplitude, frequency and timing can be varied separately. **Amplitude** here means the maximum magnitude of the ideal wave relative to its centre. **Frequency** counts cycles per second, measured in **hertz (Hz)**. A 2 Hz wave repeats twice per second.

**Phase** tells us where in the cycle a wave starts. An angle in **radians** measures arc length divided by radius. A full turn is twice pi radians; pi is about 3.14159. A quarter turn is half pi radians. At zero starting phase, sine starts at zero and rises; cosine starts at its positive maximum.

## A wave sampled at regular instants

Use a sine function whose input is an angle in radians. The expression inside sine advances the angle as the index increases.

```formula
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
In words: The sine’s angle advances by a fixed amount each sample, while amplitude scales its height.
```

A unit-amplitude 1 Hz sine at 4 samples per second, starting at zero phase, gives approximately `[0, 1, 0, -1]` for its first four samples. The next sample would begin the next cycle. Changing amplitude scales these values; changing phase moves the starting point around the cycle. A finite set of samples need not hit the ideal wave’s maximum.

> [!analogy] Real-world analogy: A hand on a clock
> Picture a hand turning at a steady rate.
>
> **How it maps:** Its turning rate represents frequency and its starting direction represents phase. The vertical height of its tip behaves like a sine wave.
>
> **Where it stops:** The rotating hand is a geometric aid; a measured signal does not need to be a physical rotating object.

## Frequency per sample

**Normalised frequency** must name its convention. Here it means cycles per sample; some other texts instead use radians per sample or a fraction of the Nyquist frequency. Never transfer a bare number between these conventions.

```formula
ν = f / F_s
ω = 2πν
ν = (1 Hz) / (4 / s) = 0.25
ω = 0.5π
where
ν: normalised frequency, in cycles per sample, here 0.25
f: frequency, in hertz (Hz)
F_s: sample rate, in samples per second
ω: angle advance, in radians per sample, here half pi
π: pi, about 3.14159
Hz: hertz, one cycle per second
s: second, the unit of time
In words: One quarter of a cycle per sample advances the angle by a quarter turn each time.
```

This complete standard-library example calculates the four samples above. `math.sin` expects radians. `round` makes tiny numerical residues display as zero; floating-point arithmetic does not make every theoretical zero exact.

```python
import math
fs, freq, amp = 4.0, 1.0, 1.0
phase = 0.0
x = [amp * math.sin(
    2 * math.pi * freq * n / fs + phase)
    for n in range(4)]
print([round(v, 6) for v in x])
# [0.0, 1.0, 0.0, -1.0]
```

A waveform’s appearance alone is insufficient: the same sequence played or interpreted at another sample rate has another physical frequency. Sampling also creates ambiguities, explored next.

## Key takeaways
- Amplitude controls height, frequency controls repetition and phase controls the cycle’s starting point.
- Sine and cosine functions in Python use radians.
- Always label a normalised-frequency convention.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH8.PDF)
