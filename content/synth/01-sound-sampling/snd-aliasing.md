---
id: snd-aliasing
title: Nyquist and aliasing
level: intermediate
minutes: 15
summary: The sampling theorem and the Nyquist frequency, how to calculate where an alias lands, why sharp synth waveforms alias, and what anti-aliasing and reconstruction filters do.
---

Sampling has a hard limit. Above a certain frequency, a sampled signal stops meaning what you think it means: a 30 kHz tone and an 18 kHz tone can produce *exactly the same samples*. This is **aliasing**, and it's the most important limitation in digital synthesis.

For a synth builder it's not an abstract worry. The classic analogue waveforms (sawtooth, square, pulse) have harmonics that go on for ever. Generate them naively in software and some of those harmonics fold back into the audible range as clangy, out-of-tune tones. This lesson explains why, and how to predict exactly where they'll land.

## The sampling theorem

The **Nyquist–Shannon sampling theorem** says:

> A signal containing no frequencies at or above B can be perfectly reconstructed from its samples if the sample rate fs is greater than 2B.

Turned around, a given sample rate can represent frequencies only up to **fs/2**, the **Nyquist frequency**:

| Sample rate | Nyquist frequency |
|---|---|
| 44.1 kHz | 22.05 kHz |
| 48 kHz | 24 kHz |
| 96 kHz | 48 kHz |

"Perfectly reconstructed" is a strong claim and it's true. Below Nyquist, samples aren't a rough approximation of the wave: they contain all its information. A 10 kHz sine at 48 kHz has only 4.8 samples per cycle and looks like a jagged mess on a plot, yet a correct DAC rebuilds a pure 10 kHz sine from those samples.

The condition is strict: *below* fs/2, not at it. A sine at exactly fs/2 gets sampled twice per cycle. Depending on its phase, the samples might be +1, −1, +1, −1 or 0, 0, 0, 0. They can't tell you the amplitude.

## What aliasing is

Take a sine at 30 kHz and sample it at 48 kHz. Each sample advances 30/48 = 0.625 of a cycle. Since the samples only see the phase *modulo whole cycles*, that's indistinguishable from moving back 0.375 of a cycle, which is what an 18 kHz sine does (18/48 = 0.375), only played in reverse:

```python
import numpy as np
fs = 48_000
n = np.arange(8)
hi = np.sin(2*np.pi*30_000*n/fs)
lo = np.sin(2*np.pi*18_000*n/fs)
print(np.allclose(hi, -lo))
```

```text
True
```

The 30 kHz samples equal the 18 kHz samples with the sign flipped (a phase inversion). Once sampled, nothing can tell them apart. A DAC will output 18 kHz. The 30 kHz tone has taken on an **alias**.

## Calculating the alias frequency

Picture the frequency axis folded back and forth like a paper fan, with creases at every multiple of fs/2:

```diagram
 0      fs/2      fs      3fs/2
 |--------|--------|--------|
 0 ----> 24k
         24k <---- 48k
                  48k ----> 72k
```

Any frequency maps to the point directly below it on the first segment, 0 to fs/2. As a procedure:

1. Reduce f modulo fs, giving a value from 0 up to fs.
2. If the result is above fs/2, subtract it from fs.

```python
def alias(f, fs):
    f = f % fs          # wrap into [0, fs)
    return fs - f if f > fs / 2 else f

fs = 48_000
for f in (1_000, 23_000, 30_000, 47_000,
          50_000, 97_000):
    a = alias(f, fs)
    print(f"{f:>6} Hz -> {a:>6} Hz")
```

```text
  1000 Hz ->   1000 Hz
 23000 Hz ->  23000 Hz
 30000 Hz ->  18000 Hz
 47000 Hz ->   1000 Hz
 50000 Hz ->   2000 Hz
 97000 Hz ->   1000 Hz
```

Worked through:

- **30 kHz:** 30k mod 48k = 30k, above 24k, so 48k − 30k = **18 kHz**. It folded back off the Nyquist "wall".
- **47 kHz:** just under fs. Folds to 48k − 47k = **1 kHz**: an ultrasonic tone has become a low, obvious one.
- **50 kHz:** 50k mod 48k = **2 kHz**. Just above fs it appears as a low frequency, without folding.
- **97 kHz:** 97k mod 48k = 1k. Two cycles round the fan.

Notice the behaviour as an input sweeps upwards: the alias rises to 24 kHz, then **falls** to 0 at 48 kHz, then rises again. A rising pitch whose alias falls is the unmistakable sound of aliasing.

## Why sharp waveforms alias

A sine has one frequency. A sawtooth at f has harmonics at every multiple k·f, with amplitudes 1/k. A square has the odd harmonics, also falling as 1/k. A falling rate of 1/k is slow: the 20th harmonic is still only 26 dB below the fundamental.

The cause is the waveform's **sharp edge**. A discontinuity (an instant jump) needs infinitely many harmonics to describe, and a waveform with a jump has harmonics that fall off at 1/k (6 dB per octave). A triangle wave has corners but no jumps, and its harmonics fall as 1/k² (12 dB per octave), so it aliases far less.

A **naive** sawtooth, generated directly from the phase accumulator (`saw = 2*phase − 1`), samples the ideal infinite-bandwidth sawtooth. Every harmonic above Nyquist folds back. Take a high note, 1760 Hz (A6), at 48 kHz:

- Harmonics up to k = 13 (22,880 Hz) are below 24 kHz and fine.
- Harmonics 14 and up fold back, and they **aren't at multiples of 1760 Hz**.

Which aliases land low, where they are most audible?

```python
import math

def alias(f, fs):
    f = f % fs
    return fs - f if f > fs / 2 else f

fs, f0 = 48_000, 1_760
for k in range(14, 31):
    a = alias(k * f0, fs)
    if a < 5_000:
        db = 20 * math.log10(1 / k)
        print(f"harmonic {k}: {k*f0} Hz"
              f" -> {a} Hz ({db:.1f} dB)")
```

```text
harmonic 25: 44000 Hz -> 4000 Hz (-28.0 dB)
harmonic 26: 45760 Hz -> 2240 Hz (-28.3 dB)
harmonic 27: 47520 Hz -> 480 Hz (-28.6 dB)
harmonic 28: 49280 Hz -> 1280 Hz (-28.9 dB)
harmonic 29: 51040 Hz -> 3040 Hz (-29.2 dB)
harmonic 30: 52800 Hz -> 4800 Hz (-29.5 dB)
```

Harmonic 27 lands at **480 Hz**, below the note's own fundamental, only about 29 dB down. None of these are harmonics of 1760 Hz, so they sound like an inharmonic, metallic ring. As the note bends, they slide in the wrong directions. Low notes are less affected (their high harmonics are much weaker by the time they reach Nyquist), which is why naive oscillators can sound fine in the bass and terrible at the top.

> [!warning] You can't filter it out afterwards
> Once an alias is at 480 Hz, it's indistinguishable from a real 480 Hz component. A low-pass filter after the oscillator can't remove it without removing real content too. Aliasing has to be prevented where the high frequencies are *created*.

## Preventing aliasing in a synth

There are two situations.

**1. Sampling a real analogue signal (an ADC).** Here an **anti-aliasing filter** removes content above Nyquist *before* it can fold. Every audio interface input has one. In a modern delta-sigma ADC, the converter samples many times faster than fs, so a simple analogue low-pass in front is enough, and a steep digital filter does the rest before the rate is reduced to fs.

**2. Generating a signal digitally (an oscillator).** There's no analogue signal to filter: the samples are computed directly. So the oscillator itself must only generate content below Nyquist. Established techniques, at a conceptual level:

- **Additive synthesis:** sum sines for each harmonic, stopping below Nyquist. Exact, but costly for low notes with hundreds of harmonics.
- **Band-limited wavetables:** precompute a single cycle with only the harmonics that fit, keeping several tables for different pitch ranges and picking one per note.
- **BLIT / BLEP methods:** generate the waveform naively, then smooth each discontinuity with a precomputed band-limited correction. PolyBLEP is a cheap polynomial approximation of this, light enough for small processors.
- **Oversampling:** run the oscillator at, say, 4× the output rate, low-pass filter digitally, then discard samples. Aliases still occur, but further up where harmonics are weaker, and the filter removes much of them before downsampling.

The roadmap suggests comparing a naive waveform with a library's band-limited version rather than inventing a technique. Stilson and Smith's paper in the further reading is the classic overview.

**Nonlinear processing aliases too.** Clipping, distortion, waveshaping and FM all create new harmonics. A hard clipper applied to a 5 kHz sine creates harmonics at 15, 25, 35 kHz and so on, and those above Nyquist fold back. Oversampling around the nonlinear stage is the standard remedy.

## Reconstruction: the DAC side

A DAC is given one number per sample period. A crude converter holds each value until the next (a **zero-order hold**), producing a staircase. That staircase contains the wanted signal plus **images**: copies of the spectrum mirrored around fs, 2fs, and so on. A 1 kHz tone at 48 kHz produces images at 47 and 49 kHz, 95 and 97 kHz, and so on.

A **reconstruction filter** (anti-imaging filter) removes the images, leaving the smooth wave the theorem promises. Most modern audio converters are **delta-sigma** designs that internally oversample and do much of this filtering digitally, so their external analogue filtering can be simple. Follow the converter or codec datasheet's recommended output circuit.

```flow
Analogue in
Anti-aliasing low-pass filter
ADC samples at fs
Digital processing below fs/2
DAC outputs samples
Reconstruction low-pass filter
Analogue out
```

## Key takeaways
- Sample rate fs can represent frequencies strictly below the Nyquist frequency fs/2, and does so exactly.
- A frequency above fs/2 aliases: reduce it mod fs, then if it exceeds fs/2, subtract from fs.
- Waveforms with jumps (saw, square, pulse) have harmonics falling only as 1/k, so naive versions alias badly at high pitches, producing inharmonic tones.
- Aliasing must be prevented where high frequencies are created: band-limited oscillators, oversampling around nonlinear stages. Post-filtering can't fix it.
- Anti-aliasing filters protect ADC inputs; reconstruction filters remove images from DAC outputs.

## Further reading
- [Sampling Theorem — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sampling_Theorem.html)
- [Alias-Free Digital Synthesis of Classic Analog Waveforms — Stilson & Smith (CCRMA)](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Nyquist–Shannon sampling theorem — Wikipedia](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem)
- [Aliasing — Wikipedia](https://en.wikipedia.org/wiki/Aliasing)
- [Reconstruction filter — Wikipedia](https://en.wikipedia.org/wiki/Reconstruction_filter)
- [Oversampling — Wikipedia](https://en.wikipedia.org/wiki/Oversampling)
- [Sawtooth wave — Wikipedia](https://en.wikipedia.org/wiki/Sawtooth_wave)
