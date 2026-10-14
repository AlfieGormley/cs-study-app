---
id: snd-clipping-harmonics
title: Hard and soft clipping harmonics
level: intermediate
minutes: 4
summary: Compare clipping curves and measure the new harmonics that require alias control.
sourceLesson: snd-levels
---

## Clipping: hard and soft

When a signal exceeds what a stage can represent, it **clips**.

**Hard clipping** flattens anything beyond the limit:

```formula
y = min(max(x, −1), 1)
y = min(max(1.7, −1), 1) = 1
where
y: the output sample
x: the input sample; here 1.7
max: the larger of the two values (this stops x going below −1)
min: the smaller of the two values (this stops it going above +1)
In words: values between −1 and +1 pass unchanged; anything beyond is flattened to the limit. NumPy writes this as np.clip(x, −1, 1).
```

Explicit saturating conversion does this. A raw integer cast is not a clipper: out-of-range conversion can wrap or be undefined, so clamp before converting to the DAC format. It creates a sharp corner where the wave meets the ceiling, and sharp corners mean strong high harmonics. A symmetric clip of a sine, or another input with half-wave symmetry, creates only odd harmonics before sampling. Symmetry of the clipper alone does not remove even harmonics already in an arbitrary input.

**Soft clipping** bends the wave gradually towards the limit. A common choice is the hyperbolic tangent:

```formula
y = tanh(x)
tanh(0.1) ≈ 0.0997
tanh(2.0) ≈ 0.964
where
y: the output sample, always between −1 and +1
x: the input sample, any size
tanh: the hyperbolic tangent function: an S-shaped curve that is almost a straight line near 0 and flattens out towards ±1 for large inputs
≈: approximately equal to (rounded)
In words: small values pass almost unchanged (0.1 becomes 0.0997), while large ones are squashed smoothly towards the limit (2.0 becomes 0.964).
```

Small signals pass almost unchanged; big ones are squashed smoothly. It still distorts, but its high harmonics fall away much faster.

Compare both on a 1 kHz sine driven 6 dB over full scale (amplitude 2.0). The levels are relative to the fundamental:

```python
import numpy as np

fs, f = 768_000, 1_000   # see note below
t = np.arange(fs) / fs
x = 2.0 * np.sin(2*np.pi*f*t)

# Flatten overshoots; tanh bends them.
hard = np.clip(x, -1.0, 1.0)
soft = np.tanh(x)

def harmonic_db(y, k):
    spec = np.abs(np.fft.rfft(y))
    # Here 1 Hz bins match integer hertz.
    return 20*np.log10(spec[k*f] / spec[f])

for k in (3, 5, 7, 9):
    h = harmonic_db(hard, k)
    s = harmonic_db(soft, k)
    print(f"H{k}: hard {h:6.1f}",
          f" soft {s:6.1f} dB")
```

```text
H3: hard  -12.9  soft  -15.5 dB
H5: hard  -26.9  soft  -28.3 dB
H7: hard  -35.8  soft  -40.9 dB
H9: hard  -32.9  soft  -53.4 dB
```

(The FFT reading is explained in the FFT measurement units. This experiment runs at a very high sample rate to greatly reduce alias contamination of the harmonics measured here. A finite sample rate cannot eliminate every alias from ideal hard clipping.)

By the 9th harmonic, soft clipping is about 20 dB cleaner. Inside a synth running at 48 kHz, both clippers' harmonics above 24 kHz will **alias**, which is why distortion stages are often oversampled.

> [!tip] Clipping as a sound
> Deliberate saturation is a classic synth effect. Accidental clipping at the output is a fault. The difference is whether you chose where it happens and controlled its aliasing.

## Key takeaways

- Hard clipping flattens over-range samples; a raw integer cast is not a safe clipper.
- Soft clipping bends smoothly and usually produces weaker high harmonics for comparable drive.
- Both introduce nonlinear harmonics; control aliasing around intentional distortion stages.

## Further reading

- [Clipping (audio) — Wikipedia](https://en.wikipedia.org/wiki/Clipping_(audio))
