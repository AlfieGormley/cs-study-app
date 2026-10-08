---
id: snd-levels
title: Level, decibels and headroom
level: intermediate
minutes: 20
summary: Amplitude and power decibels, dBFS, peak vs RMS and crest factor, what happens when you sum signals, hard and soft clipping, and how to stage gain inside a digital synth.
---

A synth that's too quiet is annoying. One that clips is broken: harsh, aliasing distortion every time a chord gets loud. Managing level is a constant job, from the first oscillator to the final converter, and decibels are the language for it.

## Why decibels

Level ratios in audio span an enormous range. The loudest signal a 24-bit converter handles is millions of times larger in amplitude than its quietest. Ratios like that are unreadable as plain numbers, and our perception of loudness is roughly logarithmic anyway, so audio uses a logarithmic unit: the **decibel** (dB).

A decibel is always a **ratio** to something. There are two formulas, and mixing them up is the most common mistake. For quantities that measure power or energy:

```formula
L = 10 × log_10(P_2 / P_1)
L = 10 × log_10(2) ≈ +3.01 dB
where
L: the level change, in decibels (dB); positive means louder
log_10: the base-10 logarithm, which answers "10 to what power gives this number?" (log_10(100) = 2)
P_1: the reference power (any unit, such as watts, W)
P_2: the power being compared, in the same unit as P_1; here twice P_1
dB: decibels, tenths of a bel
≈: approximately equal to (rounded)
In words: ten times the logarithm of the power ratio gives decibels, so doubling the power is about +3 dB.
```

For amplitudes (sample values, voltages, sound pressures):

```formula
L = 20 × log_10(A_2 / A_1)
L = 20 × log_10(2) ≈ +6.02 dB
where
L: the level change, in decibels (dB)
log_10: the base-10 logarithm
A_1: the reference amplitude (a sample value, or volts, V)
A_2: the amplitude being compared, in the same unit; here twice A_1
dB: decibels
≈: approximately equal to (rounded)
In words: twenty times the logarithm of the amplitude ratio gives decibels, so doubling an amplitude is about +6 dB.
```

Why the different factors? Power is proportional to amplitude squared, and the logarithm of a square is twice the logarithm:

```formula
P ∝ A^2
10 × log_10(A_2^2 / A_1^2)
= 20 × log_10(A_2 / A_1)
where
P: power
A: amplitude
∝: "is proportional to": doubling the right side doubles the left
A_2^2 / A_1^2: the power ratio written with amplitudes, because powers go as amplitude squared
log_10: the base-10 logarithm; log_10(x^2) = 2 × log_10(x)
In words: the power formula applied to squared amplitudes is the amplitude formula, so both give the same decibels for the same change.
```

Both formulas give the **same** dB value for the same change; you just use the one matching the quantity you have. Samples, voltages and pressures are **amplitudes**, so in synth code you'll nearly always use **20·log10**.

Going back from decibels to a multiplier undoes the logarithm:

```formula
g = 10^(L / 20)
g = 10^(−6 / 20) ≈ 0.501
where
g: the amplitude multiplier (gain factor) to apply to the samples; no unit
L: the level change, in decibels (dB); here −6 dB
10^x: 10 raised to the power x, the inverse of log_10
≈: approximately equal to (rounded)
In words: divide the decibels by 20 and raise 10 to that power; −6 dB means multiply the samples by about 0.5.
```

The same two conversions in Python:

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

Memorise a few: **doubling an amplitude adds about 6 dB**, **×10 adds 20 dB**, and **×1.414 (the square root of 2) adds about 3 dB**. In power terms, doubling power is +3 dB. Gains in dB **add** where the ratios multiply:

```formula
L = L_1 + L_2
L = −6 + (−12) = −18 dB
g = 10^(−18 / 20) ≈ 0.126
where
L: the total gain of two stages in a row, in decibels (dB)
L_1: the first stage's gain, in dB; here −6
L_2: the second stage's gain, in dB; here −12
g: the total amplitude multiplier
10^x: 10 raised to the power x
dB: decibels
≈: approximately equal to (rounded)
In words: chaining a −6 dB stage and a −12 dB stage gives −18 dB, the same as multiplying 0.501 by 0.251 to get about 0.126.
```

## dBFS: decibels relative to full scale

**dBFS** measures a digital level relative to the largest value the format can hold. With floats in ±1.0, full scale is 1.0, so the reference amplitude in the decibel formula is 1:

```formula
L = 20 × log_10(|x| / 1.0)
L = 20 × log_10(0.5) ≈ −6.02 dBFS
where
L: the level, in decibels relative to full scale (dBFS)
log_10: the base-10 logarithm
x: a sample value (or a peak value), with ±1.0 as full scale; here 0.5
|x|: the absolute value of x, its size ignoring the sign
dBFS: decibels relative to full scale; 0 dBFS is the largest value the format can hold
≈: approximately equal to (rounded)
In words: compare a value with full scale (1.0) on the decibel scale; anything smaller than full scale gets a negative number.
```

0 dBFS is the maximum. Everything legal is negative: a peak of 0.5 is −6 dBFS, a peak of 0.1 is −20 dBFS. A value of 2.0 would be +6 dBFS: fine inside a float pipeline, but it will clip at the converter.

> [!note] RMS and dBFS conventions differ
> For **peak** levels, dBFS is unambiguous. For **RMS** levels, conventions differ. AES17 (and related IEC and ITU standards) defines the RMS of a full-scale *sine* as 0 dBFS, so a full-scale square wave reads +3 dBFS. Other meters use the plain maths, where a full-scale sine reads −3 dBFS RMS. When comparing figures, check which convention a meter or datasheet uses. This lesson uses the plain maths.

## Peak, RMS and crest factor

Two measurements describe a signal's level:

- **Peak level:** the largest absolute sample value. It decides whether you clip.
- **RMS (root mean square):** the square root of the average of the squared samples. It tracks the signal's power, and relates more closely to perceived loudness than peak does.

The name describes the recipe, read from right to left: square every sample, take the mean, then the square root.

```formula
RMS = √((1 / N) × Σ x[n]^2)
where
RMS: root mean square, the signal's "average size" in the power sense, in the same units as the samples
N: the number of samples measured (ideally a whole number of cycles)
Σ: sigma, "add up": sum the following over every sample n from the first to the Nth
x[n]: sample number n
n: the sample index
√: square root
In words: square each sample (making them all positive), average the squares, and take the square root to get back to the samples' units.
```

For a sine, the result is always its peak divided by about 1.414 (the square root of 2):

```formula
RMS = A / √2
RMS = 0.5 / 1.414 ≈ 0.354
where
RMS: the root-mean-square value of the sine
A: the sine's peak amplitude; here 0.5
√2: the square root of 2, about 1.414
≈: approximately equal to (rounded)
In words: a sine spends most of its time below its peak, so its RMS is about 71% of the peak.
```

The ratio of peak to RMS is the **crest factor**, often given in dB:

```formula
CF = A_pk / RMS
CF_dB = 20 × log_10(A_pk / RMS)
CF_dB = 20 × log_10(1.414) ≈ 3.01 dB
where
CF: the crest factor, a plain ratio (no unit)
CF_dB: the crest factor in decibels (dB)
dB: decibels
A_pk: the peak value, the largest absolute sample
RMS: the root-mean-square value
log_10: the base-10 logarithm
≈: approximately equal to (rounded)
In words: the crest factor says how spiky a signal is: how far its peaks stand above its average level. For a sine it is about 1.414, or 3 dB.
```

| Waveform | Crest factor | In dB |
|---|---|---|
| Square | 1 | 0 |
| Sine | 1.414 (square root of 2) | 3.01 |
| Saw, triangle | 1.732 (square root of 3) | 4.77 |
| Real music | much higher | about 12–20 |

A square wave and a sine with the same peak don't sound equally loud: the square has 3 dB more RMS. If you switch an oscillator from sine to square at the same peak level, it gets louder. Synths often compensate per waveform.

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

Explicit saturating conversion does this. A raw integer cast is not a clipper: out-of-range conversion can wrap or be undefined, so clamp before converting to the DAC format. It creates a sharp corner where the wave meets the ceiling, and sharp corners mean strong high harmonics. A symmetric clip creates odd harmonics.

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

Converting either unit to an RMS voltage is the decibel formula run backwards, with that unit's reference voltage:

```formula
V = V_ref × 10^(L / 20)
V = 0.7746 × 10^(4 / 20) ≈ 1.228 V
V = 1 × 10^(−10 / 20) ≈ 0.316 V
where
V: the RMS voltage, in volts (V)
V_ref: the reference voltage: 0.7746 V for dBu, 1 V for dBV
L: the level, in dBu or dBV; here +4 dBu and −10 dBV
10^x: 10 raised to the power x
dBu: decibels relative to 0.7746 V RMS
dBV: decibels relative to 1 V RMS
≈: approximately equal to (rounded)
In words: +4 dBu is 4 dB above 0.7746 V, about 1.228 V RMS; −10 dBV is 10 dB below 1 V, about 0.316 V RMS.
```

These are *nominal* levels; real signals peak well above them, and equipment has headroom for that. Check both the synth's maximum output and the interface input's maximum level in their manuals, and set the synth's output level so that its loudest patch doesn't overload the input.

> [!warning] Keep to line-level connections
> Line, instrument, microphone, headphone and speaker connections are not interchangeable. Never connect a power amplifier's speaker output to a line input or to a development board. Work only with low-voltage, battery or USB-powered circuits and the board's documented audio outputs, and add any output protection the board's documentation recommends.

## Key takeaways
- Amplitude decibels are 20 times the base-10 logarithm of the ratio; power decibels are 10 times. ×2 amplitude ≈ +6 dB.
- dBFS is relative to full scale: 0 dBFS is the maximum, normal levels are negative. RMS dBFS conventions differ.
- Crest factor is peak divided by RMS: 3 dB for a sine, 0 dB for a square.
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
