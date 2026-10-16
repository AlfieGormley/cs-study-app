---
id: syn-oscillators-phase-wrap
title: Wrapping phase without losing overshoot
level: basic
minutes: 4
summary: Wrapping phase without losing overshoot.
sourceLesson: syn-oscillators
---

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
                # Bug: the overshoot
                # disappears.
                p = 0.0
            else:
                p -= 1.0
    # Mean includes the last partial
    # alignment.
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
e = 1200 log_2(f_out / f)
e = 1200 log_2(1090.9 / 1100) ≈ −14
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

So resetting makes every 1100 Hz cycle exactly 44 samples, giving 1090.9 Hz: about 14 cents flat, an audible error. The error is worst for high notes, where one extra sample is a large part of a short cycle. Subtracting 1 keeps the fraction, so cycle lengths vary between 43 and 44 samples and approach the requested average pitch in exact arithmetic; finite measurements and floating-point arithmetic introduce small errors.

Two more wrapping cases matter:

- **Increment of 1 or more** (a very high frequency or extreme modulation): one subtraction is not sufficient for every such overshoot (for example, an overshoot above two cycles). Use `p = p - floor(p)`.
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

Wrapping does not make frequencies above Nyquist representable. The floor method is a finite-number range operation: reject NaN/infinity, and do not infer numerical accuracy once enormous phases have already lost their fractional bits.

## Key takeaways

- Reset-to-zero wrapping discards overshoot and detunes the oscillator.
- Subtracting the floor wraps finite positive and negative phases into one cycle.

## Further reading

- [Digital sinusoid generators — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Digital_Sinusoid_Generators.html)
- [C11 committee draft — WG14](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python mathematical functions — Python](https://docs.python.org/3/library/math.html)
