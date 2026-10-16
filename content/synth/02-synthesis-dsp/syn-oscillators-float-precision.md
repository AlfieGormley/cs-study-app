---
id: syn-oscillators-float-precision
title: Why growing floating-point phase drifts
level: basic
minutes: 5
summary: Why growing floating-point phase drifts.
sourceLesson: syn-oscillators
---

## Floating-point precision drift

Single-precision `float` has a 24-bit significand, about 7 significant decimal digits. That matters in two ways.

**Wrapped phase in float is fine.** Running a float32 accumulator at 440 Hz for a simulated minute gave 439.99972 Hz on average, an error of about 0.001 cents. The phase stays below 1, where floats are precise.

**Unwrapped phase in float is a bug.** If you never wrap, or compute each sample directly from a growing sample counter like this:

```formula
y[n] = sin((2πfn) / f_s)
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
        # Actual next step at this
        # magnitude.
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

The note goes audibly out of tune within seconds and wildly wrong after a few minutes. The reason is the spacing between neighbouring normal float32 values, which doubles when the magnitude crosses the next power-of-two boundary. The ideal unwrapped phase after 60 seconds would be about 26,400 cycles. The accumulated float32 phase differs, but remains in the same binary-exponent interval in this run:

```formula
gap = 2^{(e − 23)}
gap = 2^{14 − 23} = 2^{−9} ≈ 0.00195
inc_f = round(inc / gap) × gap
inc_f = round(0.0091667 / 0.00195) × gap
inc_f = round(4.69) × gap = 5 × 0.00195
inc_f ≈ 0.00977
f_eff = inc_f f_s
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

## Key takeaways

- Float32 spacing grows with magnitude, so an unwrapped accumulator changes its effective step.
- Wrapped phase keeps the number small; a growing float32 counter eventually cannot count every sample.

## Further reading

- [Floating-point limits — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.finfo.html)
- [Python mathematical functions — Python](https://docs.python.org/3/library/math.html)
