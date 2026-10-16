---
id: snd-wrapped-phase-state
title: Keep a wrapped phase accumulator
level: basic
minutes: 5
summary: Preserve phase through frequency changes and processing blocks without an ever-growing counter.
sourceLesson: snd-waves
---

## The phase accumulator

The sampled sine equation in the preceding unit recomputes phase from the sample index each time. Many real oscillators instead keep the **phase of a wave** in a running variable and add the increment each sample, wrapping it back into range after each full cycle:

```python
import math

fs, f = 48_000, 440.0
inc = f / fs
phase = 0.0          # cycles, in [0, 1)
out = []
for n in range(6):
    # Read the wave at the current phase.
    out.append(math.sin(2*math.pi*phase))
    phase += inc
    # Wrap after one full cycle.
    if phase >= 1.0:
        phase -= 1.0
print([round(x, 4) for x in out])
```

```text
[0.0, 0.0576, 0.1149, 0.1719, 0.2284, 0.284]
```

This **phase accumulator** is the core of many digital oscillators. It has three advantages over recomputing from n.

**1. Frequency changes preserve phase.** Recomputing `sin(2π·f·t)` with a new f can make the phase jump. Switch from 440 Hz to 450 Hz at 0.525 s:

```python
import math
fs = 48_000
t = 25_200 / fs      # 0.525 s
# Reusing absolute time changes the phase.
before = math.sin(2*math.pi*440*t)
after  = math.sin(2*math.pi*450*t)
print(f"{before:.3f} -> {after:.3f}")
```

```text
0.000 -> 1.000
```

At the switch time, the two formulas give values of 0 and full scale. Switching directly between them can introduce an abrupt waveform jump and an audible click; the exact adjacent samples and audibility depend on the switch and playback conditions. With an accumulator, you just change `inc` and the phase carries on from where it was. Vibrato, pitch bends and glides can use this. An abrupt increment change can still make a transient by changing the waveform’s slope; ramping the increment makes the transition gentler.

**2. Precision stays bounded.** The phase is always between 0 and 1, so its spacing stays bounded instead of getting coarser with elapsed time. Rounding of the increment and additions can still introduce a small frequency error. A sample counter n only grows. A 32-bit float (common on embedded chips) represents integers exactly only up to 2²⁴ = 16,777,216. At 48 kHz that's about 349.5 seconds, under six minutes. After that, `n + 1 == n` in float32, and an oscillator that computes from n starts to drift and distort.

**3. It's cheap.** One add and a compare per sample, then a waveform lookup. The waveform part can be `sin`, a table, or simple arithmetic for a sawtooth (the phase itself, rescaled, *is* a naive saw).

> [!warning] Keep the state between blocks
> Audio is processed in blocks (say 48 samples at a time). The phase must persist from one block to the next. Resetting it to zero each block repeats the same 48-sample segment. At 48 kHz, that repeated segment has a 1 kHz repetition rate, with spectral components on a 1 kHz grid, rather than the intended 440 Hz sine. Boundaries can jump and the result can buzz or click; the exact spectrum and audibility depend on the waveform, reset timing and playback conditions.

## Why absolute-time glides go wrong

Frequency is the rate at which phase advances. If you multiply a changing frequency by all the elapsed time, earlier cycles are effectively recalculated at the new frequency. For a linear glide, the resulting frequency has an extra term:

```formula
f_eff(t) = f(t) + t × r
r = (880 − 440) / 0.1 = 4400 Hz/s
f_eff(10.05) = 660 + 10.05 × 4400
f_eff(10.05) = 44880 Hz
where
f_eff(t): the instantaneous frequency produced by using f(t) times absolute time as the phase in cycles, in hertz (Hz)
f(t): the requested frequency at time t, in hertz; here a linear glide from 440 to 880 Hz between 10.0 and 10.1 seconds
r: the rate at which the requested frequency changes during the glide, in hertz per second (Hz/s)
t: absolute elapsed time, in seconds (s)
Hz: hertz, cycles per second
Hz/s: hertz per second
In words: the incorrect formula adds elapsed time times the glide’s slope to the requested pitch, producing 44,880 Hz halfway through this glide instead of 660 Hz.
```

This follows from the rate of change of a product: both frequency and elapsed time are changing. An accumulator adds each sample’s current increment to the phase already earned. It therefore follows the requested frequency sample by sample, subject to ordinary rounding error.

## Pitfalls

- **Ignoring wrap.** Without the wrap, a float phase eventually loses precision like the counter does.

## Key takeaways

- Keep phase as oscillator state and add the current increment for every sample.
- Changing the increment preserves phase; recomputing from absolute time can cause jumps.
- Wrap phase to keep numerical spacing bounded, and retain it between audio blocks. Rounding error still remains.

## Further reading

- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Numerically controlled oscillator (phase accumulator) — Wikipedia](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
- [Changing frequency requires accumulated phase — CMU Introduction to Computer Music](https://www.cs.cmu.edu/~music/icm-online/readings/fm-synthesis/index.html)
