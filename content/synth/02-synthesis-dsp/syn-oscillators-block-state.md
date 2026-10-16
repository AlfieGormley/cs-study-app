---
id: syn-oscillators-block-state
title: Keeping phase across audio blocks
level: basic
minutes: 3
summary: Keeping phase across audio blocks.
sourceLesson: syn-oscillators
---

This offline example stores phase in an object and returns newly allocated Python lists. It illustrates persistent DSP state, not real-time memory handling. The single-subtraction wrap assumes a positive frequency below the sample rate; useful audio fundamentals must also respect Nyquist.

## State carried across blocks

Here is a minimal oscillator that processes a block at a time. The phase lives in the object, not in the function:

```python
import math

class Osc:
    def __init__(self, fs):
        self.fs = fs
        self.phase = 0.0  # cycles, [0,1)

    def process(self, freq, n):
        # Frequency sets cycles
        # advanced/sample.
        inc = freq / self.fs
        out = []
        for _ in range(n):
            w = 2 * math.pi * self.phase
            out.append(math.sin(w))
            # Advance after emitting this
            # sample.
            self.phase += inc
            if self.phase >= 1.0:
                # Keep the fractional
                # overshoot.
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
φ = (nf) / f_s
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
> If phase resets at every block with constant frequency and identical processing, the same block repeats. With 64-sample blocks at 48 kHz, the output is periodic on a 750 Hz harmonic grid; it generally replaces the intended tone rather than adding a separate buzz to it. Some frequencies happen to fit an integer number of cycles per block, so do not use one favourable test to establish correctness.

## Key takeaways

- Phase belongs to the oscillator, so the next block continues the same sequence.
- Resetting every block can replace the intended tone with the block repetition spectrum.

## Further reading

- [Digital sinusoid generators — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Digital_Sinusoid_Generators.html)
- [Waveform implementation — PJRC](https://raw.githubusercontent.com/PaulStoffregen/Audio/3039be2773e86daf1f381a1e8bdc1e6a55ed11f1/synth_waveform.cpp)
