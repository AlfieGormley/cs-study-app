---
id: snd-polyphonic-headroom
title: Summing voices and budgeting headroom
level: intermediate
minutes: 4
summary: Predict in-phase and unrelated sums and compare safe voice scaling with average-level scaling.
sourceLesson: snd-levels
---

## Summing signals

Mixing digital signals is just addition, sample by sample. What happens to the level depends on how the signals relate:

- **Identical, in phase:** amplitudes add. Two equal signals give +6.02 dB.
- **Identical, with opposite polarity:** they cancel.
- **Unrelated** (different frequencies, noise): **powers** add. Two equal signals give about +3 dB of RMS.

The distinction grows as more sources are added:

With unrelated equal-level voices, RMS grows more slowly than the worst-case peak: three voices add about 4.8 dB of RMS on average, whereas three identical aligned copies add about 9.5 dB. Average power does not bound the largest sample.

But peaks are what clip, and unrelated signals still line up their peaks now and then. Here's an A major triad, each voice a sine at 0.8 (−1.9 dBFS):

```python
import numpy as np

fs = 48_000
t = np.arange(fs) / fs
voices = [0.8*np.sin(2*np.pi*f*t)
          for f in (220, 277.18, 329.63)]
# Add corresponding samples of all voices.
mix = sum(voices)

def dbfs(v):
    return 20 * np.log10(v)

peak = np.max(np.abs(mix))
# Square, average, then take the root.
rms = np.sqrt(np.mean(mix**2))
for name, v in [("peak", peak),
                ("rms ", rms)]:
    print(f"{name} {v:.2f}",
          f"({dbfs(v):+.1f} dBFS)")
print("samples over 1.0:",
      np.sum(np.abs(mix) > 1.0))
```

```text
peak 2.40 (+7.6 dBFS)
rms  0.98 (-0.2 dBFS)
samples over 1.0: 15337
```

The RMS rose by the expected amount for three unrelated signals:

One of these voices has RMS about 0.566. Three together have RMS about 0.98, as expected for unrelated equal-level signals over this capture.

But the three peaks nearly align, reaching about 2.4. Converted to a fixed format, almost a third of the samples would clip.

**Headroom** is the gap between your normal peak level and 0 dBFS. Two common policies scale each voice by the voice count or its square root. They serve different goals.

- Assuming each voice is bounded by full scale, dividing each by the maximum voice count bounds the mathematical sum at full scale, but makes single notes quiet.
- Dividing by the square root of the voice count keeps average RMS steadier for unrelated voices but can still peak over. Many designs do this and add a soft clipper or limiter at the end to catch the rare peaks.

> [!analogy] Real-world analogy: Several taps feeding one drain
> A drain can carry the flow from any one tap, yet simultaneous surges from several taps can exceed its flow capacity. Average flow alone does not describe a brief surge.
>
> **How it maps:** Tap flow rates are simultaneous voice sample values, and drain flow capacity is the output range. The sample values add, so aligned peaks can exceed that range even when individual voices and average RMS look modest.
>
> **Where it stops:** Audio values can be positive or negative and can cancel; water flow in this picture cannot. RMS power addition also follows signal statistics, rather than adding average tap flows directly.

## Key takeaways

- Identical in-phase signals add amplitudes; unrelated signals add power on average.
- Unrelated signals can still align their peaks and exceed full scale.
- Dividing by voice count protects against the worst case; square-root scaling needs protection for overshoots.

## Further reading

- [Decibel — Wikipedia](https://en.wikipedia.org/wiki/Decibel)
- [dBFS — Wikipedia](https://en.wikipedia.org/wiki/DBFS)
- [Gain stage — Wikipedia](https://en.wikipedia.org/wiki/Gain_stage)
- [Decibels and signal combination — UNSW](https://www.phys.unsw.edu.au/jw/dB.html)
