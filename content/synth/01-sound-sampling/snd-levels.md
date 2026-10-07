---
id: snd-levels
title: Level, decibels and headroom
level: intermediate
minutes: 15
summary: Amplitude and power decibels, dBFS, peak vs RMS and crest factor, what happens when you sum signals, hard and soft clipping, and how to stage gain inside a digital synth.
---

A synth that's too quiet is annoying. One that clips is broken: harsh, aliasing distortion every time a chord gets loud. Managing level is a constant job, from the first oscillator to the final converter, and decibels are the language for it.

## Why decibels

Level ratios in audio span an enormous range. The loudest signal a 24-bit converter handles is millions of times larger in amplitude than its quietest. Ratios like that are unreadable as plain numbers, and our perception of loudness is roughly logarithmic anyway, so audio uses a logarithmic unit: the **decibel** (dB).

A decibel is always a **ratio** to something. There are two formulas, and mixing them up is the most common mistake:

```text
power ratio:     dB = 10 · log10(P2 / P1)
amplitude ratio: dB = 20 · log10(A2 / A1)
```

Why the different factors? Power is proportional to amplitude squared (P ∝ V², for example), and log10(x²) = 2·log10(x). Both formulas give the **same** dB value for the same change; you just use the one matching the quantity you have. Samples, voltages and pressures are **amplitudes**, so in synth code you'll nearly always use **20·log10**.

```python
import math

def amp_db(ratio):
    return 20 * math.log10(ratio)

def db_amp(db):
    return 10 ** (db / 20)

for r in (2, 0.5, 10, 0.1, 1.4142):
    d = amp_db(r)
    print(f"x{r:<6} -> {d:+6.2f} dB")
for db in (-3, -6, -12, -20):
    print(f"{db:+} dB -> x{db_amp(db):.3f}")
```

```text
x2      ->  +6.02 dB
x0.5    ->  -6.02 dB
x10     -> +20.00 dB
x0.1    -> -20.00 dB
x1.4142 ->  +3.01 dB
-3 dB -> x0.708
-6 dB -> x0.501
-12 dB -> x0.251
-20 dB -> x0.100
```

Memorise a few: **×2 amplitude ≈ +6 dB**, **×10 = +20 dB**, **×√2 ≈ +3 dB**. In power terms, doubling power is +3 dB. Gains in dB **add** where the ratios multiply: a −6 dB stage followed by a −12 dB stage is −18 dB, a factor of about 0.126.

## dBFS: decibels relative to full scale

**dBFS** measures a digital level relative to the largest value the format can hold. With floats in ±1.0, full scale is 1.0, so:

```text
level in dBFS = 20 · log10(|x|)
```

0 dBFS is the maximum. Everything legal is negative: a peak of 0.5 is −6 dBFS, a peak of 0.1 is −20 dBFS. A value of 2.0 would be +6 dBFS: fine inside a float pipeline, but it will clip at the converter.

> [!note] RMS and dBFS conventions differ
> For **peak** levels, dBFS is unambiguous. For **RMS** levels, conventions differ. AES17 (and related IEC and ITU standards) defines the RMS of a full-scale *sine* as 0 dBFS, so a full-scale square wave reads +3 dBFS. Other meters use the plain maths, where a full-scale sine reads −3 dBFS RMS. When comparing figures, check which convention a meter or datasheet uses. This lesson uses the plain maths.

## Peak, RMS and crest factor

Two measurements describe a signal's level:

- **Peak:** the largest absolute sample value. It decides whether you clip.
- **RMS (root mean square):** the square root of the average of the squared samples. It tracks the signal's power, and relates more closely to perceived loudness than peak does.

Their ratio is the **crest factor** (peak/RMS), often given in dB:

| Waveform | Crest factor | In dB |
|---|---|---|
| Square | 1 | 0 |
| Sine | √2 ≈ 1.414 | 3.01 |
| Saw, triangle | √3 ≈ 1.732 | 4.77 |
| Real music | much higher | about 12–20 |

A square wave and a sine with the same peak don't sound equally loud: the square has 3 dB more RMS. If you switch an oscillator from sine to square at the same peak level, it gets louder. Synths often compensate per waveform.

## Summing signals

Mixing digital signals is just addition, sample by sample. What happens to the level depends on how the signals relate:

- **Identical, in phase:** amplitudes add. Two equal signals give +6.02 dB. N give 20·log10(N) dB.
- **Identical, 180° out of phase:** they cancel.
- **Unrelated** (different frequencies, noise): **powers** add. Two equal signals give about +3 dB of RMS; N give about 10·log10(N) dB.

But peaks are what clip, and unrelated signals still line up their peaks now and then. Here's an A major triad, each voice a sine at 0.8 (−1.9 dBFS):

```python
import numpy as np

fs = 48_000
t = np.arange(fs) / fs
voices = [0.8*np.sin(2*np.pi*f*t)
          for f in (220, 277.18, 329.63)]
mix = sum(voices)

def dbfs(v):
    return 20 * np.log10(v)

peak = np.max(np.abs(mix))
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

The RMS rose by the expected 10·log10(3) ≈ 4.8 dB (each voice's RMS is 0.8/√2 ≈ 0.566, so 0.566·√3 ≈ 0.98). But the peaks hit the worst case, 3 × 0.8 = 2.4. Converted to a fixed format, almost a third of the samples would clip.

**Headroom** is the gap between your normal peak level and 0 dBFS. For an N-voice synth:

- Scaling each voice by 1/N (−20·log10 N dB) guarantees no overflow. For 8 voices that's −18.1 dB, which makes single notes quiet.
- Scaling by 1/√N (−10·log10 N dB, −9.0 dB for 8 voices) keeps average loudness steadier but can still peak over. Many designs do this and add a soft clipper or limiter at the end to catch the rare peaks.

## Clipping: hard and soft

When a signal exceeds what a stage can represent, it **clips**.

**Hard clipping** flattens anything beyond the limit: `y = clip(x, −1, 1)`. Explicit saturating conversion does this. A raw integer cast is not a clipper: out-of-range conversion can wrap or be undefined, so clamp before converting to the DAC format. It creates a sharp corner where the wave meets the ceiling, and sharp corners mean strong high harmonics. A symmetric clip creates odd harmonics.

**Soft clipping** bends the wave gradually towards the limit, for example `y = tanh(x)`. Small signals pass almost unchanged; big ones are squashed smoothly. It still distorts, but its high harmonics fall away much faster.

Compare both on a 1 kHz sine driven 6 dB over full scale (amplitude 2.0). The levels are relative to the fundamental:

```python
import numpy as np

fs, f = 768_000, 1_000   # see note below
t = np.arange(fs) / fs
x = 2.0 * np.sin(2*np.pi*f*t)

hard = np.clip(x, -1.0, 1.0)
soft = np.tanh(x)

def harmonic_db(y, k):
    spec = np.abs(np.fft.rfft(y))
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

(The FFT reading is explained in lesson 6. This experiment runs at a very high sample rate so that the clipper's harmonics don't alias and contaminate the measurement.)

By the 9th harmonic, soft clipping is about 20 dB cleaner. Inside a synth running at 48 kHz, both clippers' harmonics above 24 kHz will **alias**, which is why distortion stages are often oversampled.

> [!tip] Clipping as a sound
> Deliberate saturation is a classic synth effect. Accidental clipping at the output is a fault. The difference is whether you chose where it happens and controlled its aliasing.

## Gain staging inside a digital synth

**Gain staging** means setting the level at each stage so that no stage clips and none is needlessly quiet. In a floating-point synth, intermediate stages almost never clip, so the concerns are different from analogue gear:

```flow
Oscillators, each about -6 to -12 dBFS
Voice mixer: scale for the number of sources
Filter: resonance can boost near cutoff
Amp envelope and velocity
Voice sum: scale for polyphony
Effects: check for level build-up
Master gain, then soft clip or limiter
Convert to the codec format (hard limit)
```

Practical rules:

1. **Know where the hard limit is.** In a float pipeline it's the final conversion. Everything before can exceed 1.0 temporarily.
2. **Budget headroom where levels can grow:** summing voices, resonant filters (which can boost signals near the cutoff well above the input level) and feedback effects.
3. **Protect the output.** A soft clipper or limiter just before conversion turns rare overshoots into mild saturation instead of harsh clipping.
4. **Measure.** Log peak and RMS in an offline render of your worst case: all voices, full resonance, maximum velocity.
5. **Change gain smoothly.** Jumping a gain value between samples causes clicks; stepping it in coarse increments when a knob turns causes "zipper noise". Smoothing is covered in the synthesis module.

## From dBFS to volts

The DAC turns 0 dBFS into some maximum output voltage. That voltage is set by the codec and the output circuit, so it's on the board's datasheet, not a universal number. What your audio interface expects is in its manual. Two common nominal **line levels** use different references:

| Level | Reference | RMS voltage |
|---|---|---|
| +4 dBu (pro) | 0 dBu = 0.7746 V | ≈ 1.228 V |
| −10 dBV (consumer) | 0 dBV = 1 V | ≈ 0.316 V |

These are *nominal* levels; real signals peak well above them, and equipment has headroom for that. Check both the synth's maximum output and the interface input's maximum level in their manuals, and set the synth's output level so that its loudest patch doesn't overload the input.

> [!warning] Keep to line-level connections
> Line, instrument, microphone, headphone and speaker connections are not interchangeable. Never connect a power amplifier's speaker output to a line input or to a development board. Work only with low-voltage, battery or USB-powered circuits and the board's documented audio outputs, and add any output protection the board's documentation recommends.

## Key takeaways
- Amplitude dB = 20·log10(ratio); power dB = 10·log10(ratio). ×2 amplitude ≈ +6 dB.
- dBFS is relative to full scale: 0 dBFS is the maximum, normal levels are negative. RMS dBFS conventions differ.
- Crest factor = peak/RMS: 3 dB for a sine, 0 dB for a square.
- In-phase sums add amplitudes (+6 dB for two), unrelated signals add power (+3 dB), but peaks can still add up fully.
- Hard clipping makes strong high harmonics that alias; soft clipping makes fewer. Put the hard limit only at the final conversion and protect it.
- Check output and input levels against the exact equipment manuals.

## Further reading
- [Decibel — Wikipedia](https://en.wikipedia.org/wiki/Decibel)
- [dBFS — Wikipedia](https://en.wikipedia.org/wiki/DBFS)
- [Crest factor — Wikipedia](https://en.wikipedia.org/wiki/Crest_factor)
- [Line level — Wikipedia](https://en.wikipedia.org/wiki/Line_level)
- [Clipping (audio) — Wikipedia](https://en.wikipedia.org/wiki/Clipping_(audio))
- [Gain stage — Wikipedia](https://en.wikipedia.org/wiki/Gain_stage)
