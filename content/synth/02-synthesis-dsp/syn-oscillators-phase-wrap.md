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

With reset-to-zero, each cycle lasts the ideal number of samples rounded **up** to a whole number. The output therefore repeats too slowly unless the requested cycle already fits a whole number of samples.


So resetting makes every 1100 Hz cycle exactly 44 samples, giving 1090.9 Hz: about 14 cents flat, an audible error. The error is worst for high notes, where one extra sample is a large part of a short cycle. Subtracting 1 keeps the fraction, so cycle lengths vary between 43 and 44 samples and approach the requested average pitch in exact arithmetic; finite measurements and floating-point arithmetic introduce small errors.

Two more wrapping cases matter:

- **Increment of 1 or more** (a very high frequency or extreme modulation): one subtraction is not sufficient for every such overshoot (for example, an overshoot above two cycles). Use `p = p - floor(p)`.
- **Negative increments** (through-zero FM, reversed playback): the phase can go below 0, so wrap upwards too. `p - floor(p)` handles both directions. Beware that some languages' remainder operators (such as C's `fmod`) return negative results for negative inputs.

Here is why `p - floor(p)` works in both directions:

```formula essential
p_w = p − floor(p)
where
p_w: the wrapped phase, always from 0 up to (not including) 1
p: the phase before wrapping, in cycles; it may be above 1 or below 0
floor: rounds down to a whole number, always towards minus infinity, so floor(2.4) = 2 and floor(−0.3) = −1
In words: Subtract complete cycles, rounding down, to retain a position from zero up to one cycle. This also wraps negative phase upwards while keeping its fractional position.
```

Wrapping does not make frequencies above Nyquist representable. The floor method is a finite-number range operation: reject NaN/infinity, and do not infer numerical accuracy once enormous phases have already lost their fractional bits.

> [!analogy] Real-world analogy: Keeping your place on a running track
> After passing the start line, a runner keeps the distance travelled beyond it.
>
> **How it maps:** A whole lap is one cycle. Wrapping removes completed laps while retaining the overshoot; resetting to zero throws away progress.
>
> **Where it stops:** Digital phase advances in discrete steps and does not model physical inertia. Wrapping cannot prevent spectral aliasing.

## Key takeaways

- Reset-to-zero wrapping discards overshoot and detunes the oscillator.
- Subtracting the floor wraps finite positive and negative phases into one cycle.

## Further reading

- [Digital sinusoid generators — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Digital_Sinusoid_Generators.html)
- [C11 committee draft — WG14](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Python mathematical functions — Python](https://docs.python.org/3/library/math.html)
