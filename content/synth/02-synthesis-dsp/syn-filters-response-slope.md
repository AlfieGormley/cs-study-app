---
id: syn-filters-response-slope
title: Frequency response, cutoff and slope
level: intermediate
minutes: 3
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

To estimate how much a low-pass cuts a frequency well above its cutoff, count the octaves and multiply by the slope.

A steeper stopband slope reduces distant harmonics more strongly for the same frequency ratio. For example, three octaves above cutoff means three doublings, not three extra hertz. Compare measured response curves when exact rejection matters.

This is an asymptote (the straight line the curve approaches): near the cutoff, and with resonance, the real curve differs, so use it only for frequencies well above cutoff.

A steep slope separates low and high content more sharply; a gentle slope leaves more upper harmonics. Neither is inherently more natural: choose for the target sound.

## Key takeaways

- An LTI filter scales and phase-shifts steady sine components.
- Use per-pole slope as a qualified asymptotic rule, not a universal digital response formula.

## Further reading

- [Introduction to digital filters — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/)
- [Audio EQ Cookbook — Robert Bristow-Johnson / W3C](https://www.w3.org/TR/audio-eq-cookbook/)
