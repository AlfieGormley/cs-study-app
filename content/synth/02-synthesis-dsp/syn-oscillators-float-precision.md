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

**Wrapping protects precision in these examples.** Running a float32 accumulator at 440 Hz for a simulated minute gave 439.99972 Hz on average, an error of about 0.001 cents. The phase stays below 1, where floats are precise.

**Unwrapped phase in float is a bug.** If you never wrap, the stored number grows without limit. A growing floating-point sample counter converted to an ever-larger angle has the same broad risk: its spacing eventually becomes too coarse to represent small changes accurately.

This experiment isolates repeated phase addition:

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

The note goes audibly out of tune within seconds and wildly wrong after a few minutes. The reason is the spacing between neighbouring normal float32 values, which doubles when the magnitude crosses the next power-of-two boundary. The ideal unwrapped phase after 60 seconds would be about 26,400 cycles. The accumulated float32 phase differs, but remains in the same binary-exponent interval in this run.

Near the phase reached after a minute in this example, adjacent float32 values are about 0.002 cycles apart. The intended step is about 0.0092 cycles, so addition rounds it to about 0.0098. The actual phase step has changed, which changes the pitch.

That matches the measured 468.8 Hz. The spacing grows at successive powers of two. Rounding can move the step up or down: after 300 seconds the simulated frequency is 375 Hz. Separately, a float32 counter repeatedly incremented by one can stall at 16,777,216, about 5.8 minutes at 48 kHz, because the next integer is no longer representable. A drone or a held pad would expose this on stage. Always keep phase wrapped to one cycle (or use the integer form).

Wrapping means keeping the fractional cycle progress when phase crosses a cycle boundary. Resetting phase to zero at each audio block instead discards progress and can create a discontinuity. Preserve phase between blocks; a frequency change normally changes the increment while leaving the current phase intact.

## Key takeaways

- Float32 spacing grows with magnitude, so an unwrapped accumulator changes its effective step.
- Wrapped phase keeps the number small; a growing float32 counter eventually cannot count every sample.

## Further reading

- [Floating-point limits — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.finfo.html)
- [Python mathematical functions — Python](https://docs.python.org/3/library/math.html)
