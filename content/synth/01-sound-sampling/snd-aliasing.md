---
id: snd-aliasing
title: Nyquist and aliasing
level: intermediate
minutes: 19
summary: The sampling theorem and the Nyquist frequency, how to calculate where an alias lands, why sharp synth waveforms alias, and what anti-aliasing and reconstruction filters do.
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

The 30 kHz samples equal the 18 kHz samples with the sign flipped (a phase inversion). Once sampled, nothing can tell them apart. A DAC will output 18 kHz. The 30 kHz tone has taken on an **alias frequency**, or alias.

## Calculating the alias frequency

Picture the frequency axis folded back and forth like a paper fan, with creases at every multiple of the Nyquist frequency (fs/2 in the drawing, where fs is the sample rate):

```diagram
 0      fs/2      fs      3fs/2
 |--------|--------|--------|
 0 ----> 24k
         24k <---- 48k
                  48k ----> 72k
```

Any frequency maps to the point directly below it on the first segment, from 0 up to the Nyquist frequency. As a procedure:

1. Divide the frequency by the sample rate and keep the remainder (this is "modulo"), giving a value from 0 up to the sample rate.
2. If the result is above the Nyquist frequency, subtract it from the sample rate.

As a formula:

```formula
r = f mod fs
f_a = min(r, fs − r)
r = 30000 mod 48000 = 30000
f_a = min(30000, 18000) = 18000 Hz
where
f: the true frequency being sampled, in hertz (Hz); here 30 kHz
fs: the sample rate, in hertz (Hz); here 48 kHz
mod: "modulo": the remainder after removing as many whole multiples of fs as possible (50,000 mod 48,000 is 2,000)
r: the frequency after wrapping into the range 0 up to fs
min: the smaller of the two values
f_a: the alias, the frequency that actually appears after sampling, between 0 and fs/2, in hertz (Hz)
Hz: hertz, cycles per second
In words: wrap the frequency into one sample-rate's width, then, if it lands in the top half, reflect it down off the Nyquist frequency. 30 kHz sampled at 48 kHz appears at 18 kHz.
```

The formula holds for any frequency, sine by sine. A complex sound is a sum of sines, so apply it to each component separately.

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

A sine has one frequency. A sawtooth has harmonics at every whole-number multiple of its frequency, and their amplitudes fall slowly:

```formula
f_k = k × f_0
a_k = 1 / k
L_k = 20 × log_10(1 / k)
L_20 = 20 × log_10(1 / 20) ≈ −26 dB
where
f_k: the frequency of harmonic number k, in hertz (Hz)
k: the harmonic number, a whole number 1, 2, 3, …; k = 1 is the fundamental
f_0: the fundamental frequency of the note, in hertz (Hz)
a_k: the amplitude of harmonic k, relative to the fundamental
L_k: the level of harmonic k relative to the fundamental, in decibels (dB)
L_20: that level for the 20th harmonic
log_10: the base-10 logarithm; 20 × log_10 of an amplitude ratio gives decibels (lesson 5)
dB: decibels
≈: approximately equal to (rounded)
In words: harmonic k is k times the frequency and has 1/k of the amplitude, so even the 20th harmonic is only about 26 dB quieter than the fundamental.
```

A square has only the odd harmonics (1st, 3rd, 5th, …), whose amplitudes also fall as one over the harmonic number. That fall-off is slow, so a lot of energy sits in very high harmonics.

The cause is the waveform's **sharp edge**. A discontinuity (an instant jump) needs infinitely many harmonics to describe, and a waveform with a jump has harmonics that fall off at 1/k (6 dB per octave). A triangle wave has corners but no jumps, and its harmonics fall as 1/k² (12 dB per octave), so it aliases far less.

A **naive sawtooth** is generated directly from the phase accumulator (lesson 1) by rescaling the phase:

```formula
s = 2 × p − 1
where
s: the sawtooth output sample, from −1 to +1
p: the oscillator phase, in cycles, from 0 up to 1 (it wraps back to 0 every cycle)
In words: stretch the phase from 0..1 to −1..+1. The output ramps up and then jumps straight back down when the phase wraps.
```

That jump makes it a sample of the ideal infinite-bandwidth sawtooth. Every harmonic above Nyquist folds back. Take a high note, 1760 Hz (A6), at 48 kHz:

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

**1. Sampling a real analogue signal (an ADC).** Here an **anti-aliasing filter** removes content above Nyquist *before* it can fold. Every audio interface input has one. In a modern delta-sigma ADC, the converter samples many times faster than the final sample rate, so a simple analogue low-pass in front is enough, and a steep digital filter does the rest before the rate is reduced to the final rate.

**2. Generating a signal digitally (an oscillator).** There's no analogue signal to filter: the samples are computed directly. So the oscillator itself must only generate content below Nyquist. Established techniques, at a conceptual level:

- **Additive synthesis:** sum sines for each harmonic, stopping below Nyquist. Exact, but costly for low notes with hundreds of harmonics.
- **Band-limited wavetables:** precompute a single cycle with only the harmonics that fit, keeping several tables for different pitch ranges and picking one per note.
- **BLIT / BLEP methods:** generate the waveform naively, then smooth each discontinuity with a precomputed band-limited correction. PolyBLEP is a cheap polynomial approximation of this, light enough for small processors.
- **Oversampling:** run the oscillator at, say, 4× the output rate, low-pass filter digitally, then discard samples. Aliases still occur, but further up where harmonics are weaker, and the filter removes much of them before downsampling.

The roadmap suggests comparing a naive waveform with a library's band-limited version rather than inventing a technique. Stilson and Smith's paper in the further reading is the classic overview.

**Nonlinear processing aliases too.** Clipping, distortion, waveshaping and FM all create new harmonics. A hard clipper applied to a 5 kHz sine creates harmonics at 15, 25, 35 kHz and so on, and those above Nyquist fold back. Oversampling around the nonlinear stage is the standard remedy.

## Reconstruction: the DAC side

A DAC is given one number per sample period. A crude converter holds each value until the next (a **zero-order hold**), producing a staircase. That staircase contains the wanted signal plus **images** (**image frequencies**): copies of the spectrum mirrored around every multiple of the sample rate.

```formula
f_img = m × fs ± f
f_img = 1 × 48 − 1 = 47 kHz
f_img = 1 × 48 + 1 = 49 kHz
where
f_img: the frequency of an image component, in kilohertz (kHz) here
m: a whole number 1, 2, 3, …, picking which multiple of the sample rate the image sits around
fs: the sample rate; here 48 kHz
f: the frequency of the wanted tone; here 1 kHz
±: plus or minus: each multiple gives two images, one below it and one above
kHz: kilohertz, thousands of cycles per second
In words: a 1 kHz tone played at 48 kHz also produces images at 47 and 49 kHz, then 95 and 97 kHz, and so on.
```

Images are not aliases. An alias is a wrong frequency *inside* the audio band, created when sampling; images sit *above* Nyquist, created when converting back to analogue, and a filter can remove them.

A **reconstruction filter** (anti-imaging filter) removes the images, leaving the smooth wave the theorem promises. Most modern audio converters are **delta-sigma** designs that internally oversample and do much of this filtering digitally, so their external analogue filtering can be simple. Follow the converter or codec datasheet's recommended output circuit.

```flow
Analogue in
Anti-aliasing low-pass filter
ADC samples at the sample rate
Digital processing below Nyquist
DAC outputs samples
Reconstruction low-pass filter
Analogue out
```

## Key takeaways
- A sample rate can represent frequencies strictly below the Nyquist frequency, half the sample rate, and does so exactly.
- A frequency above the Nyquist frequency aliases: take its remainder after dividing by the sample rate, then, if that is above half the sample rate, subtract it from the sample rate.
- Waveforms with jumps (saw, square, pulse) have harmonics whose amplitude falls only in proportion to one over the harmonic number, so naive versions alias badly at high pitches, producing inharmonic tones.
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
