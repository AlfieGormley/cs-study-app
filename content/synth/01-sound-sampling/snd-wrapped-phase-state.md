---
id: snd-wrapped-phase-state
title: Keep a wrapped phase accumulator
level: basic
minutes: 5
summary: Preserve phase through frequency changes and processing blocks without an ever-growing counter.
sourceLesson: snd-waves
---

## The phase accumulator

A sine can be evaluated using each sample’s elapsed time. Many real oscillators instead keep the **phase of a wave** in a running variable and add the increment each sample, wrapping it back into range after each full cycle:

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

This **phase accumulator** is the core of many digital oscillators. It has three advantages over recomputing phase from a growing sample counter.

**1. Frequency changes preserve phase.** Recomputing phase from total elapsed time with a new frequency can make the phase jump. Switch from 440 Hz to 450 Hz at 0.525 s:

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

**2. Precision stays bounded.** The phase is always between 0 and 1, so its spacing stays bounded instead of getting coarser with elapsed time. Rounding of the increment and additions can still introduce a small frequency error. A sample counter n only grows. A 32-bit float (common on embedded chips) represents integers exactly only up to 2²⁴ = 16,777,216. At 48 kHz that's about 349.5 seconds, under six minutes. At that boundary, adding one to a float32 counter can leave it unchanged. An oscillator relying on that counter can stall; other ever-growing time calculations can also lose phase accuracy.

**3. It's cheap.** One add and a compare per sample, then a waveform lookup. The waveform part can be `sin`, a table, or simple arithmetic for a sawtooth (the phase itself, rescaled, *is* a naive saw).

> [!warning] Keep the state between blocks
> Audio is processed in blocks (say 48 samples at a time). The phase must persist from one block to the next. Resetting it to zero each block repeats the same 48-sample segment. At 48 kHz, that repeated segment has a 1 kHz repetition rate, with spectral components on a 1 kHz grid, rather than the intended 440 Hz sine. Boundaries can jump and the result can buzz or click; the exact spectrum and audibility depend on the waveform, reset timing and playback conditions.

> [!analogy] Real-world analogy: A clock hand changing speed
> A clock hand can speed up without jumping to a new position. It continues from wherever it has reached.
>
> **How it maps:** The hand’s position is oscillator phase; its speed is frequency. Changing the phase increment changes future progress while keeping the current phase.
>
> **Where it stops:** An oscillator’s phase wraps every cycle, and digital updates introduce rounding. A continuous phase also does not guarantee a perfectly smooth slope when its speed changes abruptly.

## Why absolute-time glides go wrong

Frequency is the rate at which phase advances. If you multiply a changing frequency by all the elapsed time, earlier cycles are effectively recalculated at the new frequency. This is the practical failure during a glide: The oscillator can run much faster than the setting suggests, and the error depends on when the glide begins. Frequencies pushed beyond Nyquist also alias in sampled playback. Accumulating only the new phase step avoids this recalculation of the past.

An accumulator adds each sample’s current increment to the phase already earned. It therefore follows the requested frequency sample by sample, subject to ordinary rounding error.

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
