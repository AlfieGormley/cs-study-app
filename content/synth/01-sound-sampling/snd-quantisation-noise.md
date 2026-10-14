---
id: snd-quantisation-noise
title: Predict and measure quantisation noise
level: intermediate
minutes: 4
summary: Derive the full-scale-sine SQNR rule and see where coarse quantisation breaks its assumptions.
sourceLesson: snd-sampling
---

## Quantisation noise and the six-decibel rule

For a busy signal much larger than one step, the error behaves like a small random noise added to the signal: **quantisation noise**. How far that noise sits below the signal is the **SQNR**, the signal-to-quantisation-noise ratio, measured in decibels (dB, a logarithmic scale for ratios explained in the decibel-gain unit). The standard result, for a full-scale sine wave, is:

```formula
SQNR ≈ 6.02 × N + 1.76 dB
SQNR ≈ 6.02 × 16 + 1.76 dB
SQNR ≈ 98.1 dB
where
SQNR: signal-to-quantisation-noise ratio: the RMS (average) level of a full-scale sine compared with the RMS level of the rounding noise, in decibels
N: the bit depth, in bits; here 16
dB: decibels; every 6 dB is roughly a factor of 2 in amplitude
≈: approximately equal to (the formula is an approximation, and the result is rounded)
In words: each bit adds about 6 dB of distance between a full-scale sine and the quantisation noise, plus a constant 1.76 dB, so 16 bits give about 98 dB.
```

**Each extra bit adds about 6 dB**, because it halves the step size and halving an amplitude is −6.02 dB. 16 bits gives about 98 dB; 24 bits about 146 dB.

Where do the two numbers come from? The rounding error is spread evenly across one step, which gives it a predictable RMS (root-mean-square, a kind of average size; the peak-and-RMS unit). A full-scale sine spans all the steps, so its peak is half of that span, and a sine's RMS is its peak divided by about 1.414. Putting those together:

```formula
S = (2^N × Δ / 2) / √2
E = Δ / √12
S / E = 2^N × √1.5
SQNR = 20 × log_10(S / E)
SQNR = 20 × N × log_10(2)
     + 20 × log_10(√1.5)
SQNR ≈ 6.02 × N + 1.76 dB
where
S: the RMS size of the full-scale sine, in full-scale units (the same units as Δ)
SQNR: the signal-to-quantisation-noise ratio, in decibels (dB)
E: the RMS size of the quantisation error, in the same units, assuming it is spread evenly within ±Δ/2
Δ: delta, the quantisation step size
N: the bit depth, in bits
√: square root
log_10: the base-10 logarithm, used by the decibel scale; 20 × log_10 of an amplitude ratio gives decibels
dB: decibels
≈: approximately equal to (rounded)
In words: the signal-to-noise ratio is 2^N times a constant; in decibels, the 2^N becomes 6.02 dB per bit and the constant becomes 1.76 dB.
```

The derivation shows the assumptions: a sine that fills full scale without overloading, and an error that is evenly spread and unrelated to the signal. A quieter signal gets proportionally less SQNR, and very coarse quantisation breaks the second assumption.

You can check this in a few lines:

```python
import numpy as np

fs = 48_000
n = np.arange(fs)                 # 1 second
x = 0.999 * np.sin(2*np.pi*997*n/fs)

def quantise(x, bits):
    scale = 2 ** (bits - 1)  # 16 -> 32768
    # Round to the nearest integer level.
    q = np.round(x * scale)
    # Saturate at the signed endpoints.
    q = np.clip(q, -scale, scale - 1)
    return q / scale

for bits in (4, 8, 12, 16):
    # Compare quantised samples to input.
    err = quantise(x, bits) - x
    snr = 10*np.log10(np.mean(x**2)
                      / np.mean(err**2))
    pred = 6.02*bits + 1.76
    print(f"{bits:>2} bits: {snr:5.1f} dB"
          f" (formula {pred:5.1f})")
```

```text
 4 bits:  23.3 dB (formula  25.8)
 8 bits:  49.3 dB (formula  49.9)
12 bits:  74.0 dB (formula  74.0)
16 bits:  98.1 dB (formula  98.1)
```

At 12 and 16 bits the formula agrees closely. At 4 bits this example also **overloads the positive endpoint**: its largest code is 7/8, below the sine's 0.999 peak. That clipping contributes substantial error. In addition, the uniform, signal-independent error model is only an approximation; low-resolution periodic quantisation can produce distortion rather than a gentle hiss.

> [!note] Why 997 Hz?
> Test tones are often slightly "odd" frequencies like 997 Hz rather than 1000 Hz. With 1000 Hz at 48 kHz, each cycle is exactly 48 samples, so the same few quantisation errors repeat every cycle and pile up at harmonic frequencies. An odd frequency spreads them out.

## Key takeaways

- The uniform-error model predicts about 6.02 dB per bit plus 1.76 dB for a full-scale sine.
- Lower signal level reduces SQNR even when the file’s bit depth stays fixed.
- Coarse quantisation and endpoint overload can produce distortion and disagree with the noise model.

## Further reading

- [Quantization (signal processing) — Wikipedia](https://en.wikipedia.org/wiki/Quantization_(signal_processing))
- [Audio bit depth — Wikipedia](https://en.wikipedia.org/wiki/Audio_bit_depth)
- [Taking The Mystery Out of the Infamous Formula "SNR = 6.02N + 1.76dB" — Analog Devices MT-001](https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf)
