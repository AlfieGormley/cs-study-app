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
- **Identical, 180° out of phase:** they cancel.
- **Unrelated** (different frequencies, noise): **powers** add. Two equal signals give about +3 dB of RMS.

For N equal signals:

```formula
G_same = 20 × log_10(N)
G_unrel ≈ 10 × log_10(N)
G_same = 20 × log_10(3) ≈ 9.5 dB
G_unrel ≈ 10 × log_10(3) ≈ 4.8 dB
where
G_same: the level increase when N identical, in-phase signals are summed, in decibels (dB)
G_unrel: the increase in RMS level when N equal but unrelated signals are summed, in dB
N: the number of equal signals summed; here 3
dB: decibels
log_10: the base-10 logarithm
≈: approximately equal to (true on average for unrelated signals; rounded)
In words: identical signals add their amplitudes, so N of them are N times bigger; unrelated signals add their powers, so their RMS grows only by the square root of N.
```

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

```formula
RMS_1 = 0.8 / √2 ≈ 0.566
RMS_mix ≈ RMS_1 × √3
RMS_mix ≈ 0.566 × 1.732 ≈ 0.98
where
RMS_1: the RMS of one voice, a sine of peak 0.8
RMS_mix: the RMS of the three-voice mix
√: square root; √2 ≈ 1.414, √3 ≈ 1.732
≈: approximately equal to (rounded)
In words: one voice has an RMS of about 0.566, and three unrelated voices have √3 times that, about 0.98, which is the 4.8 dB rise predicted above.
```

But the peaks hit the worst case, 3 × 0.8 = 2.4. Converted to a fixed format, almost a third of the samples would clip.

**Headroom** is the gap between your normal peak level and 0 dBFS. For an N-voice synth there are two common ways to scale the voices before summing:

```formula
g_1 = 1 / N
L_1 = −20 × log_10(N)
L_1 = −20 × log_10(8) ≈ −18.1 dB
g_2 = 1 / √N
L_2 = −10 × log_10(N)
L_2 = −10 × log_10(8) ≈ −9.0 dB
where
g_1: the per-voice gain that divides by the number of voices
g_2: the per-voice gain that divides by the square root of the number of voices
L_1: g_1 expressed in decibels (dB)
L_2: g_2 expressed in decibels (dB)
N: the number of voices (polyphony); here 8
dB: decibels
√: square root
log_10: the base-10 logarithm
≈: approximately equal to (rounded)
In words: dividing by N makes even N voices in phase fit, but costs 18 dB for 8 voices; dividing by √N keeps the average loudness of a full chord about the same as one voice, at half that cost in dB.
```

- Dividing each voice by N guarantees no overflow, but makes single notes quiet.
- Dividing by the square root of N keeps average loudness steadier but can still peak over. Many designs do this and add a soft clipper or limiter at the end to catch the rare peaks.

## Key takeaways

- Identical in-phase signals add amplitudes; unrelated signals add power on average.
- Unrelated signals can still align their peaks and exceed full scale.
- Dividing by voice count protects against the worst case; square-root scaling needs protection for overshoots.

## Further reading

- [Decibel — Wikipedia](https://en.wikipedia.org/wiki/Decibel)
- [dBFS — Wikipedia](https://en.wikipedia.org/wiki/DBFS)
- [Gain stage — Wikipedia](https://en.wikipedia.org/wiki/Gain_stage)
