---
id: syn-oscillators
title: Oscillators and the phase accumulator
level: basic
minutes: 13
summary: How a digital oscillator keeps track of phase across audio blocks, turns frequency into a phase increment, shapes sine, saw, square, triangle and pulse waves, wraps phase correctly and avoids precision drift.
---

An oscillator's job sounds trivial: output a repeating waveform at a chosen frequency. The interesting part is *state*. Audio arrives in blocks (say 32 or 48 samples at a time), the frequency may change between or within blocks, and the oscillator must continue exactly where it left off. Get the state wrong and you hear clicks, buzzes and detuning.

Nearly every digital oscillator is built on one idea: the **phase accumulator**.

## Phase as a fraction of a cycle

Represent **phase** as a number in `[0, 1)`: how far through the current cycle you are. 0 is the start of a cycle, 0.5 is halfway, and 1.0 wraps back to 0.

Each sample, advance the phase by the **phase increment**:

```
inc = f / fs        (cycles per sample)
```

At `fs = 48,000` Hz and `f = 440` Hz, `inc = 0.0091667`. After about 109 samples (48,000 / 440) the phase has gone round once, so the output repeats 440 times per second.

A waveform is then just a function of phase:

```python
import math

def sine(p):
    return math.sin(2 * math.pi * p)

def saw(p):              # rises -1 -> 1
    return 2.0 * p - 1.0

def square(p):
    return 1.0 if p < 0.5 else -1.0

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

### Pulse width

A **pulse** wave is high for a fraction `width` of each cycle. At 0.5 it is a square wave. Narrower widths sound thinner and more nasal; **pulse-width modulation** (sweeping the width with an LFO) gives a chorus-like movement. Avoid widths of exactly 0 or 1: the wave becomes a constant (DC) and goes silent.

## State carried across blocks

Here is a minimal oscillator that processes a block at a time. The phase lives in the object, not in the function:

```python
import math

class Osc:
    def __init__(self, fs):
        self.fs = fs
        self.phase = 0.0  # cycles, [0,1)

    def process(self, freq, n):
        inc = freq / self.fs
        out = []
        for _ in range(n):
            w = 2 * math.pi * self.phase
            out.append(math.sin(w))
            self.phase += inc
            if self.phase >= 1.0:
                self.phase -= 1.0
        return out

osc = Osc(48000)
a = osc.process(1000, 64)
b = osc.process(1000, 64)     # next block
print(round(osc.phase, 6))
print(round(a[-1], 4), round(b[0], 4))
```

Output:

```
0.666667
0.9239 0.866
```

After 128 samples at 1 kHz, the phase is `128 × 1000 / 48000 = 2.6667` cycles, so 0.6667 after wrapping. The last sample of block A and the first of block B are consecutive points on the same sine.

> [!warning] The block-boundary bug
> If `phase` were a local variable reset to 0 in each `process` call, every block would restart the waveform. At a 64-sample block size that is a discontinuity 750 times a second (48,000 / 64), heard as a buzz at 750 Hz on top of the tone. The roadmap's first oscillator exercise exists to make you get this right.

## Frequency control

Musical pitch is exponential: each octave doubles the frequency. MIDI note numbers convert with the 12-tone equal temperament formula (from module 1):

```
f = 440 * 2 ** ((note - 69) / 12)
```

Note 60 (middle C) is 261.63 Hz. Pitch modulation, pitch bend and detune are added in *semitones* or *cents* before this conversion, then the increment is recomputed. Because the increment is just `f / fs`, it can change every sample without any glitch: the phase simply advances faster or slower from wherever it is.

## Wrapping the phase correctly

When the phase passes 1.0, **subtract 1**. Don't reset it to 0.

Setting it to 0 discards the fraction that overshot, so each cycle becomes a whole number of samples long. That quietly detunes the oscillator:

```python
fs, f = 48000, 1100
inc = f / fs

def mean_period(reset_to_zero, cycles=1000):
    p, n, wraps = 0.0, 0, 0
    while wraps < cycles:
        p += inc
        n += 1
        if p >= 1.0:
            wraps += 1
            if reset_to_zero:
                p = 0.0
            else:
                p -= 1.0
    return n / cycles   # samples/cycle

for r in (True, False):
    T = mean_period(r)
    print(r, round(T, 3), round(fs / T, 1))
```

```
True 44.0 1090.9
False 43.637 1100.0
```

Resetting to zero makes every 1100 Hz cycle exactly 44 samples, giving 1090.9 Hz: about 14 cents flat, an audible error. Subtracting 1 keeps the fraction, so cycle lengths vary between 43 and 44 samples and average out to exactly the right pitch.

Two more wrapping cases matter:

- **Increment of 1 or more** (a very high frequency or extreme modulation): a single subtraction is not enough. Use `p = p - floor(p)`.
- **Negative increments** (through-zero FM, reversed playback): the phase can go below 0, so wrap upwards too. `p - floor(p)` handles both directions. Beware that some languages' remainder operators (such as C's `fmod`) return negative results for negative inputs.

## Integer phase accumulators

Hardware and many embedded libraries use an unsigned 32-bit integer for phase, where the full range 0 to 2³² − 1 represents one cycle. Integer overflow then *is* the wrap, for free and with no drift:

```
inc  = round(f * 2**32 / fs)
phase = (phase + inc) mod 2**32
index = phase >> (32 - table_bits)
```

The frequency resolution is `fs / 2³²`, about 0.000011 Hz at 48 kHz. This is the **numerically controlled oscillator** at the heart of direct digital synthesis (DDS) chips, and the PJRC Teensy Audio Library's waveform object uses a `uint32_t` phase accumulator in the same way (source checked 2026-10-04).

## Floating-point precision drift

Single-precision `float` has a 24-bit significand, about 7 significant decimal digits. That matters in two ways.

**Wrapped phase in float is fine.** Running a float32 accumulator at 440 Hz for a simulated minute gave 439.99972 Hz on average, an error of about 0.001 cents. The phase stays below 1, where floats are precise.

**Unwrapped phase in float is a bug.** If you never wrap (or compute `sin(2π·f·n/fs)` from a growing sample counter `n`), the number grows, and floats get coarser as they grow. The increment gets rounded to the coarse spacing:

```python
import numpy as np

fs, f = 48000, 440.0
inc = np.float32(f / fs)
p = np.float32(0.0)          # never wrapped
for sec in range(1, 301):
    for _ in range(fs):
        p = np.float32(p + inc)
    if sec in (1, 10, 60, 300):
        step = np.float32(p + inc) - p
        hz = float(step) * fs
        print(sec, round(hz, 1))
```

| Time running | Effective pitch |
|---|---|
| 1 s | 439.5 Hz |
| 10 s | 445.3 Hz |
| 60 s | 468.8 Hz |
| 300 s | 375.0 Hz |

The note goes audibly out of tune within seconds and wildly wrong after a few minutes. A drone or a held pad would expose this on stage. Always keep phase wrapped to one cycle (or use the integer form).

## From oscillator to instrument

A practical oscillator also needs:

- **Band-limiting** for saw, square and pulse, or high notes alias badly (lesson 4).
- **Smoothed or per-sample frequency** so pitch changes don't step audibly (lesson 5).
- A **reset policy**: resetting phase on each note-on gives a consistent attack; free-running sounds more like analogue oscillators. Both are valid choices.

Libraries such as DaisySP (`Oscillator`) and the Teensy Audio Library (`AudioSynthWaveform`) provide band-limited waveforms and a way to set or reset phase. Neither smooths frequency changes for you (both simply recompute the increment when you set a new frequency, as checked in their source on 2026-10-04), so smoothing remains your job. The roadmap suggests writing your own sine oscillator first, then comparing with a library's.

## Key takeaways

- Store phase as a fraction of a cycle and advance it by `f / fs` per sample.
- Phase is state: keep it in the oscillator object so blocks join seamlessly.
- Wrap by subtracting 1 (or `p - floor(p)`), never by resetting to 0, which detunes.
- Waveforms are functions of phase; pulse width sets the high fraction of the cycle.
- Unbounded float phase loses precision and drifts badly; wrapped float or 32-bit integer accumulators are stable.

## Further reading

- [Numerically controlled oscillator — Wikipedia](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
- [Direct digital synthesis — Wikipedia](https://en.wikipedia.org/wiki/Direct_digital_synthesis)
- [Single-precision floating-point format — Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
- [DaisySP Oscillator header (GitHub)](https://github.com/electro-smith/DaisySP/blob/master/Source/Synthesis/oscillator.h)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Pulse wave — Wikipedia](https://en.wikipedia.org/wiki/Pulse_wave)
