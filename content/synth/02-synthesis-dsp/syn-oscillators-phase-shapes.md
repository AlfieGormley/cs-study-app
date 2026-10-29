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

```formula essential
inc = f / f_s
where
inc: the phase increment, in cycles per sample (a fraction of one cycle)
f: the frequency you want the oscillator to play, in hertz (Hz)
f_s: the sample rate, in Hz (samples per second), e.g. 48,000; written `fs` in the code
Hz: hertz, cycles (or samples) per second
In words: The phase step is frequency divided by sample rate. Higher notes take larger steps through the cycle; doubling the sample rate requires half the step for the same note.
```

At 440 Hz and 48 kHz, the increment is about 0.0091667: one cycle takes about 109 samples, so the output repeats 440 times per second. Double the frequency and the increment doubles, so each cycle takes half as many samples.

A waveform is then just a function of phase, with phase running from zero inclusive to one exclusive.

A sine rises and falls smoothly, a saw rises then jumps down, and a triangle rises then falls along straight segments. The code below defines their phase positions precisely.

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
