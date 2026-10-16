---
id: syn-oscillators-phase-shapes
title: Phase increments and waveform shapes
level: basic
minutes: 4
summary: Phase increments and waveform shapes.
sourceLesson: syn-oscillators
---

An oscillator's job sounds trivial: output a repeating waveform at a chosen frequency. The interesting part is *state*. Audio arrives in blocks (say 32 or 48 samples at a time), the frequency may change between or within blocks, and the oscillator must continue exactly where it left off. Get the state wrong and you hear clicks, buzzes and detuning.

Many digital waveform oscillators use one idea: the **phase accumulator**.

## Phase as a fraction of a cycle

Represent **phase** as a cycle fraction from zero inclusive to one exclusive: how far through the current cycle you are. 0 is the start of a cycle, 0.5 is halfway, and 1.0 wraps back to 0.

Each sample, advance the phase by the **phase increment**: the fraction of a cycle that passes during one sample. In one second the oscillator must complete as many cycles as its frequency, while the system produces as many samples as the sample rate, so each sample covers the frequency divided by the sample rate of a cycle:

```formula
inc = f / f_s
inc = 440 Hz / 48000 Hz ≈ 0.0091667
where
inc: the phase increment, in cycles per sample (a fraction of one cycle)
f: the frequency you want the oscillator to play, in hertz (Hz)
f_s: the sample rate, in Hz (samples per second), e.g. 48,000; written `fs` in the code
≈: approximately equal to (the result is rounded)
Hz: hertz, cycles (or samples) per second
In words: each sample moves the phase on by the note's frequency divided by the sample rate, so a higher note takes bigger steps round the cycle.
```

With an increment of 0.0091667, it takes about 109 samples (48,000 / 440) for the phase to go round once, so the output repeats 440 times per second. Double the frequency and the increment doubles, so each cycle takes half as many samples.

A waveform is then just a function of phase. Written as maths, with phase running from zero inclusive to one exclusive:

```formula
y_sin = sin(2πp)
y_saw = 2p − 1
y_tri = 1 − 4|p − 0.5|
where
y_sin, y_saw, y_tri: the output sample of the sine, sawtooth and triangle waves, each between −1 and +1
p: the phase, as a fraction of a cycle from 0 up to (not including) 1
sin: the sine function; it takes an angle in radians, and one full cycle is 2π radians
π: pi, about 3.14159; multiplying by 2π turns a fraction of a cycle into an angle in radians
|x|: the absolute value of x: x without its sign, so |−0.3| = 0.3
In words: the sine turns phase into an angle; the saw rises in a straight line from −1 to +1 across the cycle; the triangle is −1 at the start, +1 halfway and −1 again at the end.
```

For example, a quarter of the way through the cycle the sine is at its peak of +1, the saw is at −0.5 and the triangle is at 0. The square and pulse waves are simpler still: +1 while the phase is below a threshold (0.5 for a square, the chosen width for a pulse), otherwise −1. In code:

```python
import math


# p is a cycle fraction; samples are
# unitless.
def sine(p):
    return math.sin(2 * math.pi * p)

def saw(p):              # rises -1 -> 1
    return 2.0 * p - 1.0

def square(p):
    return 1.0 if p < 0.5 else -1.0


# width is a high-time fraction, not
# seconds.
def pulse(p, width):     # 0 < width < 1
    return 1.0 if p < width else -1.0

def tri(p):         # -1 at 0, +1 at 0.5
    return 1.0 - 4.0 * abs(p - 0.5)
```

Separating "where am I in the cycle?" from "what value is there?" is what makes the design flexible: the same accumulator drives a sine, a wavetable lookup or an LFO.

```diagram
phase  0 ...... 0.5 ...... 1|0 ...
saw   -1  rises   0  rises  +1|-1
square +1 +1 +1 | -1 -1 -1  |+1
tri   -1   up   +1   down   -1
```

### Oscillator pulse width

A **pulse** wave is high for a fraction `width` of each cycle. At 0.5 it is a square wave. Narrower widths sound thinner and more nasal; **oscillator pulse-width modulation** (sweeping the width with an LFO) gives a chorus-like movement. Avoid widths of exactly 0 or 1: the wave becomes a constant (DC), with no sustained audible tone. Starting, stopping or changing that constant can still create a transient, and DC can use headroom; it is not a safe loudspeaker-drive signal.

## Key takeaways

- Frequency divided by sample rate gives cycles advanced per sample.
- Sine, saw, triangle and pulse are different functions of the same phase.
- Duty cycle controls oscillator pulse width; exact endpoint widths produce DC.

## Further reading

- [Digital sinusoid generators — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Digital_Sinusoid_Generators.html)
- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
