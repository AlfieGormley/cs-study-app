---
id: syn-modulation-lfo-ranges
title: LFO shapes, ranges and stepped controls
level: intermediate
minutes: 4
summary: LFO shapes, ranges and stepped controls.
sourceLesson: syn-modulation
---

A static patch sounds lifeless. **Modulation** means letting one signal change a parameter of another over time: an LFO wobbling pitch, an envelope sweeping cutoff, key velocity opening the filter. Most of a synth's expressiveness comes from what modulates what, and by how much.

This lesson covers the sources, how to scale and combine them in the right units, and where to compute them.

## LFOs

A **low-frequency oscillator** is the same phase accumulator as an audio oscillator, run below the audible pitch range. Typical rates run from well under 1 Hz (slow sweeps) to around 20 Hz (fast flutter); there's no fixed standard, and many synths go higher.

Common shapes:

- **Sine / triangle:** smooth, even wobble.
- **Saw / ramp:** repeating rise or fall.
- **Square:** switches between two values (trills).
- **Sample & hold (S&H):** a new random value each cycle, held steady.

LFOs drive controls, but their update rate still limits representable modulation; sharp shapes and modulation at audible frequencies require particular care. Slow smooth LFOs usually make aliasing less pressing than abrupt audible parameter changes. The sharp edges of a square or S&H LFO can, however, cause **clicks** if applied directly to gain or cutoff, so smooth them a little.

### Bipolar and unipolar

- **Bipolar** sources swing from −1 to +1: the parameter moves both up and down around its setting (vibrato around the note).
- **Unipolar** sources run from 0 to +1: the parameter only moves one way from its setting (tremolo that only *reduces* volume, an envelope that only opens the filter).

Convert a bipolar value to a unipolar one like this:

Shift and scale the source so its lowest value becomes zero, its centre becomes one half, and its highest value becomes one. This preserves the shape while changing the range; taking the absolute value would change the shape instead.

In the code below this is the `unipolar` function.

This offline sketch assumes a positive update rate and a non-negative LFO rate below half that update rate. It updates the held random value at a wrap; the initial held value is zero until the first wrap. Random output is nondeterministic; the printed sine/tremolo results do not use those random values.

```python
import math, random

class LFO:
    def __init__(self, rate, update_hz):
        # update_hz: how often next() runs
        # (fs, or fs / block size)
        # Phase advance per actual next()
        # call.
        self.inc = rate / update_hz
        self.p = 0.0
        self.held = 0.0

    def next(self, shape):
        p = self.p
        if shape == "sine":
            v = math.sin(2 * math.pi * p)
        elif shape == "tri":
            v = 1.0 - 4.0 * abs(p - 0.5)
        elif shape == "square":
            v = 1.0 if p < 0.5 else -1.0
        else:               # sample & hold
            v = self.held
        self.p += self.inc
        if self.p >= 1.0:
            self.p -= 1.0
            r = random.uniform(-1, 1)
            # Only wraps choose a new held
            # value.
            self.held = r
        return v                # bipolar

def unipolar(v):
    return 0.5 * (v + 1.0)      # 0..1

fs, block = 48000, 32
lfo = LFO(5.0, fs / block)      # 5 Hz
print(lfo.inc)                  # per block
depth = 0.5                     # tremolo
vals = [lfo.next("sine")
        for _ in range(300)]
gains = [1 - depth * unipolar(v)
         for v in vals]
print(round(min(gains), 3),
      round(max(gains), 3))
```

```
0.0033333333333333335
0.5 1.0
```

The LFO updates once per 32-sample block, so its increment is based on the block rate, not the sample rate.

Base the phase increment on how often the LFO actually runs. A per-block LFO takes larger steps per call than a per-sample LFO at the same musical rate; using the audio sample rate in a per-block update would make it too slow.

So the LFO updates 1,500 times a second and a 5 Hz cycle takes 300 updates. The tremolo gain swings between 0.5 and 1.0: depth 0.5 means down to half the signal amplitude, never above the original. Half amplitude is not a guarantee of half perceived loudness.

## Key takeaways

- The LFO increment uses the rate at which it is actually updated.
- Map bipolar to unipolar values when modulation should move one way.
- Smooth abrupt sample-and-hold LFO transitions if clicks are unwanted.

## Further reading

- [Blofeld user manual — Waldorf](https://downloads.waldorfmusic.com/cloud/index.php/s/32zdTsdYcRSX9eE/download)
- [Real FFT — NumPy](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
