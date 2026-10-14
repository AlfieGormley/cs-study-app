---
id: snd-wav-write-readback
title: Write WAV files and check the round trip
level: advanced
minutes: 4
summary: Export with explicit clipping and fades, then verify rate, subtype, length and quantisation error.
sourceLesson: snd-measuring
---

## Write a WAV file with a library

Writing a WAV encoder isn't a learning goal; a library handles the format. `soundfile` (a wrapper for libsndfile) takes float arrays and converts them to the requested **subtype**:

```python
import numpy as np
import soundfile as sf

fs = 48_000
n = np.arange(2 * fs)                # 2 s
# -12 dBFS sine
x = 0.25 * np.sin(2*np.pi*440*n/fs)

# 10 ms fades so the file doesn't click
ramp = np.linspace(0, 1, fs // 100)
x[:ramp.size] *= ramp
# Reverse the ramp for a smooth ending.
x[-ramp.size:] *= ramp[::-1]

x = np.clip(x, -1.0, 1.0)    # be explicit
sf.write("a440.wav", x, fs,
         subtype="PCM_24")

# Read back to check the stored result.
y, fs2 = sf.read("a440.wav")
info = sf.info("a440.wav")
print(fs2, info.subtype, len(y))
# Largest sample difference after export.
err = np.max(np.abs(y - x))
print(f"max error {err:.1e}")
```

```text
48000 PCM_24 96000
max error 1.2e-07
```

Reading the file back and comparing is the important habit. The sample rate, format and length are as intended, and the error is at most one 24-bit step (2⁻²³ ≈ 1.2 × 10⁻⁷). That's quantisation, not a bug. It's a full step rather than the half step that rounding would give because, in the libsndfile version bundled here (1.2.2), the clipping conversion rounds *down*: every error lies between 0 and −1 step. At 24 bits that's harmless, but it's exactly the kind of detail a read-back check reveals.

Notes:

- `sf.read` returns float64 in ±1.0 by default. Pass an integer type, as in `sf.read(path, dtype="int16")` (or `"int32"`), to get integers instead. These are scaled to fill the integer type, not the file's raw values: a 16-bit file read as int16 gives its stored samples, but a 24-bit file read as int32 comes back multiplied by 256.
- Use `sf.write(path, x, fs, subtype="FLOAT")` to keep a 32-bit float file with headroom above 1.0 for analysis. Use `PCM_16` or `PCM_24` for files to share or import into a DAW.
- `soundfile` switches on libsndfile's clipping option whenever it opens a file, so in testing it clipped 1.7 to full scale when writing PCM rather than wrapping it. **Clip explicitly** anyway, so your output never depends on a library setting.
- The fades matter: a file that starts or ends mid-wave clicks, which is easy to mistake for a synth bug.

## A measurement checklist

Before trusting any experiment's audio, check:

| Check | How |
|---|---|
| Length and rate | `len(x)`, `sf.info` |
| Finite values | `np.isfinite(x).all()` |
| Peak level | `np.max(np.abs(x))`, then dBFS |
| RMS and DC | `np.sqrt(np.mean(x**2))`, `np.mean(x)` |
| Full-scale warnings | `np.sum(np.abs(x) >= 1)` |
| Frequency | windowed FFT peak |
| Unwanted content | FFT, compare with prediction |

Then listen at a safe level. Measurement tells you what's there; listening tells you whether it matters.

## Key takeaways

- Use the library’s subtype to choose PCM or float storage and clip explicitly before PCM output.
- Short fades prevent start and stop discontinuities.
- Read each file back to check metadata and sample error; library versions can affect conversion details.

## Further reading

- [python-soundfile documentation](https://python-soundfile.readthedocs.io/)
