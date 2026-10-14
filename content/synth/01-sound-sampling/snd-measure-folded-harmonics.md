---
id: snd-measure-folded-harmonics
title: Measure predicted waveform aliases
level: advanced
minutes: 3
summary: Compare a naive sawtooth’s spectrum with predicted folded harmonics and recognise aliases hidden on harmonic bins.
sourceLesson: snd-measuring
---

## Verify an aliasing prediction

The sharp-waveform unit predicted where a naive 1,760 Hz sawtooth's harmonics fold at 48 kHz. Now measure it. A 1 s capture makes each bin exactly 1 Hz, so bin index equals frequency:

```python
import numpy as np

fs, f0 = 48_000, 1_760
n = np.arange(fs)                  # 1 s
phase = (f0 * n / fs) % 1.0
saw = 2 * phase - 1                # naive

w = np.hanning(fs)
X = np.fft.rfft(saw * w)
mag = np.abs(X) * 2 / w.sum()
db = 20 * np.log10(mag + 1e-12)
ref = db[f0]               # fundamental

for hz in (480, 1280, 2240, 3040, 3520):
    real = hz % f0 == 0
    kind = "harmonic" if real else "alias"
    # Level relative to the fundamental.
    rel = db[hz] - ref
    print(f"{hz:>5} Hz {rel:6.1f} dB",
          kind)
```

```text
  480 Hz  -28.5 dB alias
 1280 Hz  -28.8 dB alias
 2240 Hz  -28.2 dB alias
 3040 Hz  -29.1 dB alias
 3520 Hz   -6.0 dB harmonic
```

The predictions were −28.6, −28.9, −28.3 and −29.2 dB for the four aliases (each harmonic's amplitude is one over its harmonic number, here 27, 28, 26 and 29), and −6.0 dB for the 2nd harmonic. The measurements agree to about 0.1 dB, and the small differences come from other, much weaker harmonics folding onto the same bins. This is the "compare a deliberately aliased signal with its predicted apparent frequency" exercise from the roadmap. Later, run the same script against a band-limited oscillator from a library and watch those aliases drop.

If the sample rate is an exact multiple of a waveform’s fundamental, aliases can land on existing harmonic bins. They then change harmonic levels rather than appear as extra inharmonic lines. Test awkward frequencies as well as neat ones.

## Key takeaways

- Predict alias frequencies and relative levels before measuring the spectrum.
- Several higher harmonics can fold onto the same bin, changing its observed level.
- A neat ratio of note frequency to sample rate can hide aliases on existing harmonics; also test awkward frequencies.

## Further reading

- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [Spectrum Analysis Windows — Julius O. Smith, Spectral Audio Signal Processing (CCRMA)](https://ccrma.stanford.edu/~jos/sasp/Spectrum_Analysis_Windows.html)
