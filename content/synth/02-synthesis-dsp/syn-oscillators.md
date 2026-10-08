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

A waveform is then just a function of phase. Written as maths, with the phase p running from 0 up to 1:

```formula
y_sin = sin(2 × π × p)
y_saw = 2 × p − 1
y_tri = 1 − 4 × |p − 0.5|
where
y_sin, y_saw, y_tri: the output sample of the sine, sawtooth and triangle waves, each between −1 and +1
p: the phase, as a fraction of a cycle from 0 up to (not including) 1
sin: the sine function; it takes an angle in radians, and one full cycle is 2π radians
π: pi, about 3.14159; multiplying by 2 × π turns a fraction of a cycle into an angle in radians
|x|: the absolute value of x: x without its sign, so |−0.3| = 0.3
In words: the sine turns phase into an angle; the saw rises in a straight line from −1 to +1 across the cycle; the triangle is −1 at the start, +1 halfway and −1 again at the end.
```

For example, a quarter of the way through the cycle (p = 0.25) the sine is at its peak of +1, the saw is at −0.5 and the triangle is at 0. The square and pulse waves are simpler still: +1 while the phase is below a threshold (0.5 for a square, the chosen width for a pulse), otherwise −1. In code:

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

You can check the printed phase by hand. After n samples the phase has advanced n increments:

```formula
φ = n × f / f_s
φ = 128 × 1000 Hz / 48000 Hz ≈ 2.6667
where
φ: phi, the total phase travelled, in cycles, before wrapping
n: the number of samples processed, here two blocks of 64 = 128
f: the oscillator frequency, here 1000 Hz (1 kHz)
f_s: the sample rate, here 48,000 Hz
≈: approximately equal to
Hz: hertz, cycles per second
In words: the phase has gone round 2.6667 times; dropping the 2 whole cycles leaves 0.6667, which is what the code printed.
```

The last sample of block A and the first of block B are consecutive points on the same sine.

> [!warning] The block-boundary bug
> If `phase` were a local variable reset to 0 in each `process` call, every block would restart the waveform. At a 64-sample block size that is a discontinuity 750 times a second (48,000 / 64), heard as a buzz at 750 Hz on top of the tone. The roadmap's first oscillator exercise exists to make you get this right.

## Frequency control

Musical pitch is exponential: each octave doubles the frequency. MIDI note numbers convert to hertz with the twelve-tone equal temperament formula (from module 1):

```formula
f = 440 Hz × 2^{(m − 69)/12}
f = 440 Hz × 2^{(60 − 69)/12}
f = 440 Hz × 2^{−0.75} ≈ 261.63 Hz
where
f: the note's frequency, in hertz (Hz)
m: the MIDI note number (called `note` in code), a whole number from 0 to 127; 69 is the A above middle C and 60 is middle C
440 Hz: the reference pitch given to note 69 (A4)
12: the number of semitones in an octave; one semitone multiplies the frequency by 2^{1/12}, about 1.0595
2^{x}: 2 raised to the power x; adding 12 to m doubles f, subtracting 12 halves it
≈: approximately equal to
Hz: hertz, cycles per second
In words: count semitones away from note 69 (440 Hz) and multiply by 2 for every 12 of them.
```

So note 60 (middle C) is 261.63 Hz, and note 81 (an octave above note 69) is 880 Hz. Pitch modulation, pitch bend and detune are added in *semitones* or *cents* before this conversion, then the increment is recomputed. Because the increment is just the frequency divided by the sample rate, it can change every sample without any glitch: the phase simply advances faster or slower from wherever it is.

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

You can predict this error without running anything. With reset-to-zero, each cycle lasts the ideal number of samples rounded **up** to a whole number:

```formula
N = ⌈f_s / f⌉
N = ⌈48000 / 1100⌉ = ⌈43.64⌉ = 44
f_out = f_s / N = 48000 Hz / 44 ≈ 1090.9 Hz
e = 1200 × log_2(f_out / f)
e = 1200 × log_2(1090.9 / 1100) ≈ −14
where
N: the length of each cycle, in samples, when the phase is reset to zero
⌈x⌉: the ceiling of x: x rounded up to the next whole number, so ⌈43.64⌉ = 44
f_s: the sample rate, here 48,000 Hz
f: the frequency asked for, here 1100 Hz
f_out: the frequency actually produced, in hertz (Hz)
e: the tuning error, in cents (hundredths of a semitone); negative means flat
log_2: the base-2 logarithm: the power you raise 2 to to get the number, so log_2(2) = 1 and log_2(0.5) = −1
1200: the number of cents in an octave (12 semitones × 100 cents)
Hz: hertz, cycles per second
≈: approximately equal to
In words: resetting to zero rounds every cycle up to a whole number of samples, so the note plays flat by an amount you can work out in advance.
```

So resetting makes every 1100 Hz cycle exactly 44 samples, giving 1090.9 Hz: about 14 cents flat, an audible error. The error is worst for high notes, where one extra sample is a large part of a short cycle. Subtracting 1 keeps the fraction, so cycle lengths vary between 43 and 44 samples and average out to exactly the right pitch.

Two more wrapping cases matter:

- **Increment of 1 or more** (a very high frequency or extreme modulation): a single subtraction is not enough. Use `p = p - floor(p)`.
- **Negative increments** (through-zero FM, reversed playback): the phase can go below 0, so wrap upwards too. `p - floor(p)` handles both directions. Beware that some languages' remainder operators (such as C's `fmod`) return negative results for negative inputs.

Here is why `p - floor(p)` works in both directions:

```formula
p_w = p − floor(p)
p_w = 2.4 − floor(2.4) = 2.4 − 2 = 0.4
p_w = −0.3 − floor(−0.3) = −0.3 + 1 = 0.7
where
p_w: the wrapped phase, always from 0 up to (not including) 1
p: the phase before wrapping, in cycles; it may be above 1 or below 0
floor: rounds down to a whole number, always towards minus infinity, so floor(2.4) = 2 and floor(−0.3) = −1
In words: subtract the whole number of cycles, rounding down, which leaves only the fraction of a cycle, even for negative phases.
```

## Integer phase accumulators

Hardware and many embedded libraries use an unsigned 32-bit integer for phase, where the full range 0 to 2³² − 1 represents one cycle. Integer overflow then *is* the wrap, for free and with no drift:

```formula
N_inc = round(f × 2^{32} / f_s)
P_next = (P + N_inc) mod 2^{32}
i = floor(P / 2^{32 − b})
where
N_inc: the phase increment, as a whole number of counts per sample
P: the phase, a whole number from 0 to 2^{32} − 1 (4,294,967,295) standing for 0 up to just under one cycle
P_next: the phase on the next sample
f: the frequency wanted, in hertz (Hz)
f_s: the sample rate, in Hz
2^{32}: 4,294,967,296, the number of different values a 32-bit unsigned integer can hold
round: rounds to the nearest whole number
mod: modulo, the remainder after dividing; "mod 2^{32}" is the wrap, which a 32-bit unsigned integer does by itself when it overflows
i: the index into a wavetable (a lookup table of one cycle) that has 2^{b} entries
b: the number of index bits; a 2,048-entry table has b = 11
floor: rounds down to a whole number; dividing by 2^{32 − b} and rounding down keeps only the top b bits of P
In words: scale the frequency from cycles into counts; adding that each sample lets the register overflow to wrap, and the top bits of the phase choose the table entry.
```

For 1000 Hz at 48 kHz the increment is 1000 × 4,294,967,296 / 48,000 ≈ 89,478,485 counts per sample. In C, using the shift operator `>>` to keep the top bits:

```c
uint32_t inc = (uint32_t)llround(
    f * 4294967296.0 / fs);
phase += inc;        /* wraps at 2^32 */
uint32_t index = phase >> (32 - BITS);
```

The frequency resolution is the frequency that one count of increment represents:

```formula
f_res = f_s / 2^{32}
f_res = 48000 Hz / 4294967296 ≈ 0.000011 Hz
where
f_res: the frequency resolution: the smallest step by which the frequency can change, in hertz (Hz)
f_s: the sample rate, here 48,000 Hz
2^{32}: 4,294,967,296 counts in one cycle
≈: approximately equal to
Hz: hertz, cycles per second
In words: one count of increment is about a hundred-thousandth of a hertz, far finer than anyone can hear.
```

This is the **numerically controlled oscillator** at the heart of direct digital synthesis (DDS) chips, and the PJRC Teensy Audio Library's waveform object uses a `uint32_t` phase accumulator in the same way (source checked 2026-10-04).

## Floating-point precision drift

Single-precision `float` has a 24-bit significand, about 7 significant decimal digits. That matters in two ways.

**Wrapped phase in float is fine.** Running a float32 accumulator at 440 Hz for a simulated minute gave 439.99972 Hz on average, an error of about 0.001 cents. The phase stays below 1, where floats are precise.

**Unwrapped phase in float is a bug.** If you never wrap, or compute each sample directly from a growing sample counter like this:

```formula
y[n] = sin(2 × π × f × n / f_s)
where
y[n]: output sample number n
n: the sample counter: 0, 1, 2... counting up for ever
sin: the sine function, taking an angle in radians
π: pi, about 3.14159
f: the frequency, in hertz (Hz)
f_s: the sample rate, in Hz
In words: work out each sample's angle from how many samples have passed; correct on paper, but n and the angle grow without limit.
```

then the number grows, and floats get coarser as they grow. The increment gets rounded to the coarse spacing:

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

The note goes audibly out of tune within seconds and wildly wrong after a few minutes. The reason is the gap between neighbouring float32 values, which doubles every time the number doubles. After 60 s at about 440 Hz the unwrapped phase is roughly 60 × 440 = 26,400 cycles:

```formula
gap = 2^{e − 23}
gap = 2^{14 − 23} = 2^{−9} ≈ 0.00195
inc_f = round(inc / gap) × gap
inc_f = round(0.0091667 / 0.00195) × gap
inc_f = round(4.69) × gap = 5 × 0.00195
inc_f ≈ 0.00977
f_eff = inc_f × f_s
f_eff = 0.00977 × 48000 Hz ≈ 469 Hz
where
gap: the spacing between neighbouring float32 values near the phase, in cycles
e: the number's binary exponent: the whole number with 2^{e} ≤ the number < 2^{e+1}; 26,400 lies between 2^{14} = 16,384 and 2^{15} = 32,768, so e = 14
23: the number of stored significand (fraction) bits in float32; with the hidden leading 1 that makes 24
inc: the intended increment, 440 / 48,000 ≈ 0.0091667 cycles per sample
inc_f: the step the float addition actually makes: the increment rounded to a whole number of gaps
round: rounds to the nearest whole number
f_eff: the effective frequency produced, in hertz (Hz)
f_s: the sample rate, 48,000 Hz
≈: approximately equal to
Hz: hertz, cycles per second
In words: near 26,400 cycles a float32 can only step in units of about 0.002 cycles, so the 0.0092 increment becomes 0.0098 and the pitch rises to about 469 Hz.
```

That matches the measured 468.8 Hz. As the phase keeps growing the gap keeps doubling, which is why the error gets worse (it does not always err upwards: after 300 s the simulated phase is about 118,000 cycles, where the gap between neighbouring float32 values has grown to about 0.0078 cycles, so the increment of 0.0092 rounds *down* to a single gap, 0.0078 × 48,000 = 375 Hz). A drone or a held pad would expose this on stage. Always keep phase wrapped to one cycle (or use the integer form).

## From oscillator to instrument

A practical oscillator also needs:

- **Band-limiting** for saw, square and pulse, or high notes alias badly (lesson 4).
- **Smoothed or per-sample frequency** so pitch changes don't step audibly (lesson 5).
- A **reset policy**: resetting phase on each note-on gives a consistent attack; free-running sounds more like analogue oscillators. Both are valid choices.

Libraries such as DaisySP (`Oscillator`) and the Teensy Audio Library (`AudioSynthWaveform`) provide band-limited waveforms and a way to set or reset phase. Neither smooths frequency changes for you (both simply recompute the increment when you set a new frequency, as checked in their source on 2026-10-04), so smoothing remains your job. The roadmap suggests writing your own sine oscillator first, then comparing with a library's.

## Key takeaways

- Store phase as a fraction of a cycle and advance it by the frequency divided by the sample rate each sample.
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
