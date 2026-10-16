---
id: syn-envelopes-smoother-ramp
title: Removing zipper noise with ramps and smoothers
level: intermediate
minutes: 4
summary: Removing zipper noise with ramps and smoothers.
sourceLesson: syn-envelopes
---

## Parameter smoothing and zipper noise

Controls arrive in steps:

- A single MIDI 1.0 CC data value has 128 possible values; a sweep can cross 127 adjacent transitions. Paired high-resolution CCs and other protocols can represent more values, and not every step is necessarily audible.
- A knob read by an ADC is noisy and quantised.
- Control values often update once per audio block. At 48 kHz with 32-sample blocks, that gives up to 1,500 update opportunities a second; an unchanged target creates no step.

Each step in gain or cutoff is a small discontinuity. A sequence of them sounds like a rasping buzz while the knob moves: **zipper noise**. The fix is to let the control set a *target* and move the actual parameter towards it smoothly, every sample.

The offline code assumes positive time constant and sample rate, and a positive integer ramp length. A zero-length ramp needs a separately handled jump. These classes demonstrate the curves; they are not synchronisation mechanisms for sharing targets between real threads.

```python
import math

class OnePoleSmoother:
    def __init__(self, tau, fs, value=0.0):
        self.c = 1.0 - math.exp(
            -1.0 / (tau * fs))
        self.y = self.target = value

    def set(self, target):    # control side
        self.target = target

    def next(self):           # every sample
        y, t = self.y, self.target
        self.y = y + self.c * (t - y)
        return self.y

class LinearRamp:
    def __init__(self, n, value=0.0):
        self.n = n               # samples
        self.y = value
        self.left, self.step = 0, 0.0

    def set(self, target):
        d = target - self.y
        # Recompute from the current value.
        self.step = d / self.n
        self.left = self.n

    def next(self):
        if self.left > 0:
            self.y += self.step
            self.left -= 1
        return self.y

fs = 48000
a = OnePoleSmoother(0.005, fs)   # tau 5 ms
b = LinearRamp(240)              # 5 ms
a.set(1.0)
b.set(1.0)
ya = [a.next() for _ in range(480)]
yb = [b.next() for _ in range(480)]

# Index 239 is the 240th processed sample.
print(round(ya[239], 3), round(ya[479], 3))
print(round(yb[239], 3), round(yb[479], 3))
```

```
0.632 0.865
1.0 1.0
```

The printed values check out against the formulas. After 240 samples (5 ms, one time constant) the one-pole has covered 63.2% of the way; after 480 samples (two time constants) 86.5%. The linear ramp's step is the distance divided by its length:

```formula
Δy = (g − y_0) / N
Δy = (1.0 − 0) / 240 ≈ 0.00417
where
Δy: delta y, the change per sample
g: the target value, here 1.0
y_0: the value when the ramp starts, here 0
N: the ramp length, in samples; 240 samples is 5 ms at 48 kHz
≈: approximately equal to
In words: the ramp covers the whole distance in exactly N equal steps, then stops.
```

The one-pole smoother is the simplest option: one multiply-add per sample, one evolving output state, plus its target and coefficient, and it handles a target that keeps moving gracefully. The linear ramp finishes after its chosen sample count, reaching the target in exact arithmetic. Repeated floating-point addition can leave a small rounding error; explicitly assign the target on the last step when an exact stored endpoint is required. Its fixed duration is useful when you need a guaranteed time (e.g. a voice-steal fade before reuse) but needs recalculating whenever the target changes.

## Key takeaways

- Control updates set targets; the audio path changes parameters smoothly.
- A one-pole approaches; a fixed-length ramp reaches its target after its allotted samples.

## Further reading

- [SmoothedValue — JUCE](https://docs.juce.com/master/classSmoothedValue.html)
- [One-pole filter — Nigel Redmon](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
