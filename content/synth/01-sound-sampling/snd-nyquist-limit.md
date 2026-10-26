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

A strictly band-limited signal can be reconstructed ideally when the sample rate is more than twice its highest frequency. This requires all frequency content to remain below the boundary, including harmonics.

The practical boundary is half the sample rate, called the Nyquist frequency. At 48 kHz that boundary is 24 kHz; the signal’s content must stay strictly below it for unambiguous ideal reconstruction.

Some common rates and their boundaries:

| Sample rate | Nyquist frequency |
|---|---|
| 44.1 kHz | 22.05 kHz |
| 48 kHz | 24 kHz |
| 96 kHz | 48 kHz |

"Perfectly reconstructed" is a strong claim and it's true. Below Nyquist, samples aren't a rough approximation of the wave: they contain all its information. A 10 kHz sine at 48 kHz has only 4.8 samples per cycle and looks like a jagged mess on a plot, yet ideal reconstruction rebuilds a pure 10 kHz sine from those samples. Real DACs approximate the ideal with finite filters, finite precision and analogue noise.

The condition is strict: *below* half the sample rate, rather than at it. A sine exactly at the boundary gets sampled twice per cycle. Depending on its phase, the samples might be +1, −1, +1, −1 or 0, 0, 0, 0. They can't tell you the amplitude.

## What aliasing is

Take a sine at 30 kHz and sample it at 48 kHz. Its phase moves more than half a cycle per sample. Because whole turns leave no trace in the sine value, the samples can equally describe a lower-frequency sine moving in the opposite phase direction. At this rate, they match an inverted 18 kHz sine:

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

The 30 kHz samples equal the 18 kHz samples with the sign flipped (a phase inversion). Once sampled, nothing can tell them apart. A DAC reconstructing the baseband will output the 18 kHz component. The 30 kHz tone has taken on an **alias frequency**, or alias.

## Key takeaways

- The Nyquist frequency is half the sample rate; the reconstruction condition is strictly below it.
- A band-limited wave’s samples retain its information even when a plot looks jagged.
- Above-Nyquist tones can produce the same samples as lower tones, so their original frequency is lost.

## Further reading

- [Sampling Theorem — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sampling_Theorem.html)
- [Nyquist–Shannon sampling theorem — Wikipedia](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem)
- [Aliasing — Wikipedia](https://en.wikipedia.org/wiki/Aliasing)
