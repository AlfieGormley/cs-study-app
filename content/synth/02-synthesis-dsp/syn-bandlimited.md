---
id: syn-bandlimited
title: Band-limited oscillators
level: intermediate
minutes: 14
summary: Why naive saw and square oscillators alias, worked out with real numbers, and the established fixes (additive, mipmapped wavetables, oversampling, BLIT, BLEP and PolyBLEP), with a measured PolyBLEP-versus-naive comparison in Python.
---

The previous lesson showed that a sawtooth has harmonics at every multiple of its fundamental, forever. A digital system at sample rate `fs` can only represent frequencies below `fs/2`. Module 1 covered what happens to anything above: it **aliases**, folding back to a different frequency.

The naive oscillator from lesson 2, `2*p - 1`, samples an ideal saw directly. It therefore contains all those impossible harmonics, and they fold back into the audible band. This lesson puts numbers on the problem and shows how real synths solve it.

## Where the harmonics go

Take a high-ish note: `f0 = 1245 Hz` (close to D#6) at `fs = 48 kHz`. Nyquist is 24 kHz, so harmonics 1 to 19 (up to 23,655 Hz) are fine. Harmonic 20 is at 24,900 Hz and folds back:

```
folded = |f - k*fs|  for the nearest k

h20: 24900 -> 48000 - 24900 = 23100
h21: 26145 -> 48000 - 26145 = 21855
h31: 38595 -> 48000 - 38595 =  9405
h38: 47310 -> 48000 - 47310 =   690
h39: 48555 -> 48555 - 48000 =   555
```

| Harmonic | Lands at | Level (1/n) |
|---|---|---|
| 20 | 23,100 Hz | −26.0 dB |
| 31 | 9,405 Hz | −29.8 dB |
| 38 | 690 Hz | −31.6 dB |
| 39 | 555 Hz | −31.8 dB |

Two things make this bad:

- **The aliases are not harmonic.** 9,405 Hz and 690 Hz are not multiples of 1245 Hz, so they sound like dissonant, metallic tones rather than brightness.
- **They move the wrong way.** Bend the pitch up and a real harmonic rises, but a folded one can *fall*. Pitch sweeps produce the tell-tale "birdie" whistles moving against the note.

A component 30 dB down is clearly audible, especially at 690 Hz, where the ear is sensitive and there is little of the real tone nearby to mask it. Low notes suffer less, because their harmonics are already weak (1/n is small) by the time they reach Nyquist.

> [!note] Why square waves are no better
> The naive square has the same 1/n odd harmonics, so it aliases just as badly. A naive triangle is much better (1/n² falls faster), and a sine has nothing to alias. The problem is **discontinuities**: an instantaneous jump contains energy at all frequencies.

## Established fixes

There is no free lunch. Each method trades CPU, memory, latency or flexibility.

### 1. Additive synthesis

Sum only the harmonics below Nyquist: for this note, harmonics 1 to 19. The result is perfectly band-limited by construction. The cost is one sine per harmonic per sample: a 50 Hz note at 48 kHz has 479 harmonics below Nyquist. Fine offline, expensive for a polyphonic synth on a microcontroller.

### 2. Band-limited wavetables (mipmaps)

Precompute single-cycle tables using additive synthesis, offline. Keep several versions: one per octave (say), each containing only the harmonics that stay below Nyquist for the **highest** note that table will play. At playback, choose the table for the current pitch and read it with a phase accumulator and interpolation.

```
table for notes up to 2 kHz:
  harmonics < 24000 / 2000: max 11
table for notes up to 1 kHz:
  harmonics < 24: max 23
table for notes up to 500 Hz:
  harmonics < 48: max 47
```

This is cheap per sample and works for any waveform, which is why wavetable synths use it. The costs are memory, a slight loss of brightness at the bottom of each table's range, and possible audible switching between tables (crossfading helps). Some designs deliberately allow harmonics that fold back *above* 20 kHz, keeping more brightness at the cost of some inaudible aliasing.

### 3. Oversampling

Run the naive oscillator at a multiple of the sample rate (say 4× or 8×), low-pass filter, then discard samples (decimate). Aliases still occur, but they fold around the higher Nyquist and most of their energy is filtered out. Simple to reason about, costly in CPU, and the decimation filter must be good.

### 4. BLIT: band-limited impulse train

Stilson and Smith (CCRMA, 1996) generate a band-limited train of impulses using a closed-form formula, then **integrate** it to get a saw (or integrate a bipolar impulse train for a square). It's elegant and accurate, though the integrators need care to avoid DC drift.

### 5. BLEP and PolyBLEP: correct the jumps

Insight: a saw is smooth everywhere *except* at its jump. Aliasing comes from the jumps. So generate the naive wave, then **add a correction** around each discontinuity that turns the ideal step into a band-limited step.

- **minBLEP** (Eli Brandt, 2001) precomputes a band-limited step, makes it minimum-phase, and stores the difference from an ideal step in a table. At each jump, the oscillator adds the table, aligned to the jump's exact fractional position.
- **PolyBLEP** (Välimäki and Huovilainen, 2007) replaces the table with a tiny polynomial that only touches two samples: the one just before the jump and the one just after it. It is cheap and needs no memory, at the cost of weaker suppression than a long table.

```diagram
naive saw          PolyBLEP saw
    /|  /|             /\  /\
   / | / |            /  \/  \
  /  |/  |           /        \
 jump: 1 sample      jump spread over
 (aliases)           ~2 samples
```

## A PolyBLEP saw in Python

The polynomial below is the widely circulated two-sample PolyBLEP (as used in Martin Finke's tutorial). `t` is the phase in `[0, 1)` and `dt` the phase increment:

```python
import numpy as np

def poly_blep(t, dt):
    # t: phase [0,1), dt: increment
    if t < dt:             # just after jump
        t = t / dt
        return t + t - t * t - 1.0
    if t > 1.0 - dt:       # just before
        t = (t - 1.0) / dt
        return t * t + t + t + 1.0
    return 0.0

def saw(f0, fs, n, blep):
    dt, p = f0 / fs, 0.0
    out = np.zeros(n)
    for i in range(n):
        y = 2.0 * p - 1.0
        if blep:
            y -= poly_blep(p, dt)
        out[i] = y
        p += dt
        if p >= 1.0:
            p -= 1.0
    return out

fs, f0 = 48000, 1245     # 1 s: bin = 1 Hz
k = np.arange(fs // 2 + 1)
harm = (k % f0 == 0) & (k > 0)
low = (k > 0) & (k < 10000)
for blep in (False, True):
    x = saw(f0, fs, fs, blep)
    X = np.abs(np.fft.rfft(x)) * 2 / fs
    alias = np.where(~harm & low, X, 0)
    w = np.argmax(alias)
    db = 20 * np.log10(alias[w] / X[f0])
    h10 = 20 * np.log10(X[10 * f0] * 10
                        / X[f0])
    print("polyblep" if blep else "naive",
          w, round(db, 1), round(h10, 1))
```

Output:

```
naive 9405 -29.8 0.0
polyblep 9405 -55.4 -1.9
```

Reading it: the strongest alias below 10 kHz is at 9,405 Hz in both cases (harmonic 31 folded), but PolyBLEP pushes it from −29.8 dB to −55.4 dB relative to the fundamental, an improvement of about 25 dB. The last column is the 10th harmonic (12,450 Hz) relative to its ideal 1/n level: PolyBLEP softens it by 1.9 dB. In the same run the 19th harmonic (23.7 kHz) was 7.6 dB low. That is PolyBLEP's trade-off: it gently dulls the very top octave while removing most of the audible aliasing.

The saw's jump is downwards (+1 to −1), so the correction is *subtracted*. A square has a rising jump at phase 0 and a falling one at the pulse width `w`, so it needs two corrections:

```
y = 1 if p < w else -1
y += poly_blep(p, dt)
y -= poly_blep((p - w) mod 1, dt)
```

A quick check with the same analysis gave −55.4 dB worst alias below 10 kHz for both `w = 0.5` and `w = 0.3` (naive: −29.8 and −28.7 dB). Remember that a pulse with `w ≠ 0.5` also has a DC offset of `2w − 1`, which you may want to remove.

Triangle waves have corners, not jumps. They can be corrected with a band-limited *ramp* (BLAMP), or made by integrating a PolyBLEP square with a leaky integrator, which is what DaisySP's `WAVE_POLYBLEP_TRI` does.

## Using a library

You don't need to invent any of this. As of 2026-10-04 (GitHub master branches; confirm against current documentation):

- **DaisySP** `Oscillator` offers naive waveforms plus `WAVE_POLYBLEP_SAW`, `WAVE_POLYBLEP_SQUARE` and `WAVE_POLYBLEP_TRI`.
- **Teensy Audio Library** `AudioSynthWaveform` offers `WAVEFORM_BANDLIMIT_SAWTOOTH`, `WAVEFORM_BANDLIMIT_SAWTOOTH_REVERSE`, `WAVEFORM_BANDLIMIT_SQUARE` and `WAVEFORM_BANDLIMIT_PULSE` alongside the naive ones. Its source (`synth_waveform.cpp`, class `BandLimitedWaveform`) inserts a precomputed band-limited step from a lookup table at each edge, interpolated to the edge's fractional position and spread across a window of about 32 samples (16 either side of the edge): a table-based BLEP approach, not PolyBLEP.

The roadmap exercise is exactly this lesson's experiment: generate naive and band-limited versions at a high pitch, run them through the FFT analysis, and listen to a slow upward sweep of each.

## Choosing a method

| Method | CPU | Memory | Notes |
|---|---|---|---|
| Additive | high | low | exact; costly for low notes |
| Mipmapped tables | low | medium | any waveform |
| Oversampling | high | low | needs a good decimator |
| PolyBLEP | low | none | some top-end droop |
| minBLEP | medium | small table | better suppression |

For a first subtractive voice on a microcontroller, PolyBLEP is the usual pragmatic choice.

## Key takeaways

- Naive saw and square waves alias because their jumps contain energy above Nyquist; the folded components are inharmonic and move against pitch bends.
- Fold-back frequency is `|f − k·fs|`; at 1245 Hz and 48 kHz, harmonic 31 lands at 9,405 Hz about 30 dB down.
- Fixes: additive, mipmapped wavetables, oversampling, BLIT, minBLEP and PolyBLEP.
- PolyBLEP corrects two samples around each jump; in the test it cut the worst low alias by about 25 dB while softening the top harmonics slightly.
- Libraries (DaisySP, Teensy Audio) already provide band-limited waveforms; compare them with naive ones as an exercise.

## Further reading

- [Stilson and Smith, Alias-Free Digital Synthesis of Classic Analog Waveforms (BLIT, PDF)](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Brandt, Hard Sync Without Aliasing (minBLEP, PDF)](https://www.cs.cmu.edu/~eli/papers/icmc01-hardsync.pdf)
- [Martin Finke, PolyBLEP Oscillator](https://www.martin-finke.de/articles/audio-plugins-018-polyblep-oscillator/)
- [DaisySP Oscillator header (GitHub)](https://github.com/electro-smith/DaisySP/blob/master/Source/Synthesis/oscillator.h)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Teensy Audio Library waveform source, synth_waveform.cpp (GitHub)](https://github.com/PaulStoffregen/Audio/blob/master/synth_waveform.cpp)
- [Välimäki and Huovilainen, Antialiasing Oscillators in Subtractive Synthesis (Aalto research portal)](https://research.aalto.fi/en/publications/antialiasing-oscillators-in-subtractive-synthesis/)
- [Spectral Audio Signal Processing — Julius O. Smith, CCRMA](https://ccrma.stanford.edu/~jos/sasp/)
