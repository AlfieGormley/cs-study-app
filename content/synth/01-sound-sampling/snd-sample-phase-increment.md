---
id: snd-sample-phase-increment
title: Samples per cycle and phase increment
level: basic
minutes: 4
summary: Calculate how many samples span a cycle and how far phase advances at each sample.
sourceLesson: snd-waves
---

## From time to samples

A digital synth doesn't compute x(t) for every possible t. It computes the wave at evenly spaced instants, `fs` times per second, where `fs` is the **sample rate** (48,000 per second is typical). Sample number n happens at time n/fs seconds, so the sine formula becomes:

```formula
x[n] = A × sin(2 × π × f × n / fs + φ)
where
x[n]: the value of sample number n (square brackets mean "the sample with this index", not a continuous time)
n: the sample index, a whole number counting up from 0
fs: the sample rate, in samples per second (equivalently hertz, Hz); typically 48,000
A: the amplitude, the largest value the wave reaches
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
f: the frequency of the tone, in hertz (Hz)
φ: phi, the starting phase, in radians
In words: the sampled sine is the same formula with time replaced by "sample number divided by sample rate", which is the time at which that sample is taken.
```

Two derived numbers fall straight out of this, and the roadmap asks you to calculate both.

**Samples per period** tells you how many numbers describe one cycle:

```formula
S = fs / f
S = 48000 / 440
S ≈ 109.09
where
S: the number of samples in one cycle (samples per period); not usually a whole number
fs: the sample rate, in samples per second; here 48,000
f: the frequency of the tone, in hertz (Hz), cycles per second; here 440
≈: approximately equal to (rounded)
In words: divide samples per second by cycles per second to get samples per cycle. A 440 Hz cycle at 48 kHz spans about 109 samples.
```

**Phase increment** is how far round the cycle you move between one sample and the next. It's the reciprocal of samples per period:

```formula
Δp = f / fs
Δp = 440 / 48000
Δp ≈ 0.009167 cycles
Δθ = 2 × π × Δp ≈ 0.05760 rad
where
Δp: delta p, the phase increment in cycles per sample (the Greek letter Δ, delta, means "a step in")
Δθ: delta theta, the same increment measured in radians per sample
f: the frequency of the tone, in hertz (Hz)
fs: the sample rate, in samples per second
π: pi, about 3.14159
cycles: fractions of one full cycle
rad: radians; one full cycle is 2π radians
≈: approximately equal to (rounded)
In words: each sample moves the phase on by the frequency divided by the sample rate, in cycles; multiply by 2π to get radians.
```

The same calculation for several notes, in Python:

```python
import math

fs = 48_000
for f in (55, 440, 1000, 3520):
    # Convert rate into samples per cycle.
    spp = fs / f
    # Advance this fraction each sample.
    inc = f / fs
    rad = 2 * math.pi * inc
    print(f"{f:>4} Hz {spp:7.2f} spp"
          f" {inc:.6f} cyc {rad:.5f} rad")
```

```text
  55 Hz  872.73 spp 0.001146 cyc 0.00720 rad
 440 Hz  109.09 spp 0.009167 cyc 0.05760 rad
1000 Hz   48.00 spp 0.020833 cyc 0.13090 rad
3520 Hz   13.64 spp 0.073333 cyc 0.46077 rad
```

Notice:

- Samples per period is rarely a whole number. A 440 Hz cycle at 48 kHz takes 109.09 samples, so the samples land at slightly different points of each cycle. That's fine; the phase is tracked as a real number.
- Higher pitches get **fewer** samples per cycle. At 3520 Hz you have under 14 points per cycle. The Nyquist-limit unit shows where this runs out.
- The phase increment depends on **both** f and fs. Run the same code at 44.1 kHz and every increment changes. If a synth assumes the wrong sample rate, every note comes out at the wrong pitch.

## Pitfalls

- **Hard-coding the sample rate.** Compute the increment from the actual rate the audio hardware is running at.

## Key takeaways

- Sample time is the sample index divided by the sample rate.
- Samples per period is sample rate divided by tone frequency; it need not be a whole number.
- Phase increment is tone frequency divided by sample rate in cycles per sample. Use the hardware’s actual rate.

## Further reading

- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Numerically controlled oscillator (phase accumulator) — Wikipedia](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
