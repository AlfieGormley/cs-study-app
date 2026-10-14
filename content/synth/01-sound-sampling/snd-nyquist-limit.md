---
id: snd-nyquist-limit
title: The Nyquist limit and ambiguous samples
level: intermediate
minutes: 4
summary: Explain why sufficiently band-limited signals reconstruct exactly and why frequencies beyond Nyquist become ambiguous.
sourceLesson: snd-aliasing
---

Sampling has a hard limit. Above a certain frequency, a sampled signal stops meaning what you think it means: a 30 kHz tone and an 18 kHz tone can produce *exactly the same samples*. This is **digital aliasing**, usually just called aliasing, and it's the most important limitation in digital synthesis.

For a synth builder it's not an abstract worry. The classic analogue waveforms (sawtooth, square, pulse) have harmonics that go on for ever. Generate them naively in software and some of those harmonics fold back into the audible range as clangy, out-of-tune tones. This lesson explains why, and how to predict exactly where they'll land.



## The sampling theorem

The **Nyquist–Shannon sampling theorem** says:

> A signal containing no frequencies at or above B can be perfectly reconstructed from its samples if the sample rate fs is greater than 2B.

As a condition, and turned around into the highest frequency a given sample rate can carry:

```formula
fs > 2 × B
f_N = fs / 2
f_N = 48000 / 2 = 24000 Hz
where
fs: the sample rate, in samples per second (hertz, Hz)
B: the bandwidth: every frequency in the signal is below B, in hertz (Hz)
>: "is greater than": strictly more, not equal
f_N: the Nyquist frequency, half the sample rate, in hertz (Hz)
Hz: hertz, cycles per second
In words: you need more than two samples per cycle of the highest frequency present, so a sample rate can represent frequencies only below half of itself. At 48 kHz that limit is 24 kHz.
```

That limit, **fs/2**, is the **Nyquist frequency**:

| Sample rate | Nyquist frequency |
|---|---|
| 44.1 kHz | 22.05 kHz |
| 48 kHz | 24 kHz |
| 96 kHz | 48 kHz |

"Perfectly reconstructed" is a strong claim and it's true. Below Nyquist, samples aren't a rough approximation of the wave: they contain all its information. A 10 kHz sine at 48 kHz has only 4.8 samples per cycle and looks like a jagged mess on a plot, yet ideal reconstruction rebuilds a pure 10 kHz sine from those samples. Real DACs approximate the ideal with finite filters, finite precision and analogue noise.

The condition is strict: *below* fs/2, not at it. A sine at exactly fs/2 gets sampled twice per cycle. Depending on its phase, the samples might be +1, −1, +1, −1 or 0, 0, 0, 0. They can't tell you the amplitude.

## What aliasing is

Take a sine at 30 kHz and sample it at 48 kHz. Each sample advances 30/48 = 0.625 of a cycle. Since the samples only see the phase *modulo whole cycles*, that's indistinguishable from moving back 0.375 of a cycle, which is what an 18 kHz sine does (18/48 = 0.375), only played in reverse:

```python
import numpy as np
fs = 48_000
n = np.arange(8)
hi = np.sin(2*np.pi*30_000*n/fs)
lo = np.sin(2*np.pi*18_000*n/fs)
# True means equal samples after inversion.
print(np.allclose(hi, -lo))
```

```text
True
```

The 30 kHz samples equal the 18 kHz samples with the sign flipped (a phase inversion). Once sampled, nothing can tell them apart. A DAC will output 18 kHz. The 30 kHz tone has taken on an **alias frequency**, or alias.

## Key takeaways

- The Nyquist frequency is half the sample rate; the reconstruction condition is strictly below it.
- A band-limited wave’s samples retain its information even when a plot looks jagged.
- Above-Nyquist tones can produce the same samples as lower tones, so their original frequency is lost.

## Further reading

- [Sampling Theorem — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sampling_Theorem.html)
- [Nyquist–Shannon sampling theorem — Wikipedia](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem)
- [Aliasing — Wikipedia](https://en.wikipedia.org/wiki/Aliasing)
