---
id: syn-filters-response-slope
title: Frequency response, cutoff and slope
level: intermediate
minutes: 4
summary: Frequency response, cutoff and slope.
sourceLesson: syn-filters
---

In a subtractive synth the filter is where most of the character lives. The oscillator supplies a bright, buzzy spectrum; the filter decides how much of it you hear, and sweeping the filter is what makes a sound "open up" or "wow".

This lesson builds one filter fully (the one-pole low-pass) and introduces the resonant designs you'll use from a library, so you can choose and drive them sensibly.

## Frequency response

A linear time-invariant filter, after startup transients settle, treats each sine component separately: a sine goes in, a sine at the **same frequency** comes out, scaled in amplitude and shifted in phase. The **frequency response** says how much, for every frequency.

- **Magnitude response:** gain versus frequency, usually in dB on a log-frequency axis.
- **Phase response:** the phase shift versus frequency. A frequency-dependent phase shift is not necessarily one common time delay for the entire waveform.

Filter types by shape:

| Type | Passes | Removes |
|---|---|---|
| Low-pass | below cutoff | above cutoff |
| High-pass | above cutoff | below cutoff |
| Band-pass (BP) | around cutoff | both sides |
| Notch | both sides | around cutoff |

## Cutoff, slope and order

A **cutoff** is a design/reference frequency, often the half-power point for a simple monotonic low-pass. Filters act gradually rather than starting abruptly there; resonant or other families can use a different reference convention.

For an analogue-style all-pole low-pass, far into its stopband, each pole contributes about 6 dB per octave of asymptotic **filter slope**. This is a qualified rule: digital responses near Nyquist, zeros, shelving and other responses need their actual transfer function. The **filter order** describes the highest relevant delay or derivative after cancellation; here it corresponds to the all-pole design’s pole count:

| Order | Slope | Example family |
|---|---|---|
| 1 | 6 dB/oct | one-pole |
| 2 | 12 dB/oct | two-pole, biquad |
| 4 | 24 dB/oct | four-pole, ladder |

To estimate how much a low-pass cuts a frequency well above its cutoff, count the octaves and multiply by the slope:

```formula
S ≈ 6 dB/oct × N_p
A ≈ S × log_2(f / f_c)
A ≈ 24 dB/oct × log_2(4000 Hz / 500 Hz)
A ≈ 24 dB/oct × 3 = 72 dB
where
S: the slope well above cutoff, in decibels per octave (dB/oct)
N_p: the filter's order: its number of poles
A: the attenuation at frequency f: how much quieter the output is than the input, in decibels (dB)
log_2: the base-2 logarithm: the number of doublings (octaves) from f_c up to f
f: the frequency you are asking about, in hertz (Hz)
f_c: the cutoff frequency, in Hz
dB: decibels
oct: octave, a doubling of frequency
Hz: hertz, cycles per second
≈: approximately equal to
In words: each pole adds about 6 dB of cut per octave, and the total cut is the slope times the number of octaves above cutoff; a four-pole filter at 500 Hz cuts a 4 kHz harmonic by about 72 dB.
```

This is an asymptote (the straight line the curve approaches): near the cutoff, and with resonance, the real curve differs, so use it only for frequencies well above cutoff.

Steeper slopes sound more "synthy" and decisive; gentle slopes sound more natural.

## Key takeaways

- An LTI filter scales and phase-shifts steady sine components.
- Use per-pole slope as a qualified asymptotic rule, not a universal digital response formula.

## Further reading

- [Introduction to digital filters — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/)
- [Audio EQ Cookbook — Robert Bristow-Johnson / W3C](https://www.w3.org/TR/audio-eq-cookbook/)
