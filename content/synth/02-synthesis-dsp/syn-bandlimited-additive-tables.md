---
id: syn-bandlimited-additive-tables
title: Harmonic limits and wavetable ranges
level: intermediate
minutes: 3
summary: Harmonic limits and wavetable ranges.
sourceLesson: syn-bandlimited
---

## Established fixes

There is no free lunch. Each method trades CPU, memory, latency or flexibility.

### 1. Additive synthesis

Sum only the harmonics below Nyquist. How many is that? The largest whole number whose harmonic stays strictly below half the sample rate:

```formula reference
H = ⌈(f_s / 2) / f_0⌉ − 1
where
H: the number of harmonics that fit below Nyquist (the highest usable harmonic number)
⌈x⌉: the ceiling of x: x rounded up to the next whole number; a whole number stays as it is
f_s: the sample rate, here 48,000 Hz
f_s / 2: the Nyquist frequency, here 24,000 Hz
f_0: the note's fundamental frequency, in hertz (Hz)
In words: Keep only harmonics strictly below half the sample rate. Lower notes fit more harmonics; an exact Nyquist-frequency harmonic is excluded by this rule.
```

For a 1245 Hz note at 48 kHz, that is harmonics 1 to 19. For fixed frequencies and amplitudes, the exact sum contains only the selected below-Nyquist components. Changing amplitudes or pitch introduces sidebands that need separate checks. The cost is one sine per harmonic per sample: a 50 Hz note at 48 kHz has 479 harmonics below Nyquist. Fine offline, expensive for a polyphonic synth on a microcontroller.

### 2. Band-limited wavetables (mipmaps)

Precompute single-cycle tables using additive synthesis, offline. Keep several versions: one per octave (say), each containing only the harmonics that stay below Nyquist for the **highest** note that table will play. At playback, choose the table for the current pitch and read it with a phase accumulator and interpolation. The same counting rule sets each table's harmonic limit, using the highest note the table serves.

A table serving higher notes needs fewer harmonics. Design for the highest playback pitch in each range; a table safe only at the bottom of its range will produce above-Nyquist components as pitch rises.

Playback replaces many per-sample oscillators with table lookup and interpolation. It can represent many waveform shapes, but finite tables and interpolation can leave residual spectral error; table construction alone is not a guarantee of alias-free playback. The costs are memory, a slight loss of brightness at the bottom of each table's range, and possible audible switching between tables (crossfading helps). Some designs deliberately allow aliases confined near the top of the output band to preserve more brightness. That is a stated error tolerance, not zero aliasing or a universal inaudibility guarantee; verify the full pitch range, modulation and output chain.

> [!analogy] Real-world analogy: Packing for the smallest bag
> A shared packing list must fit the smallest bag on the trip, even if larger bags could carry more.
>
> **How it maps:** The table’s highest note has the least harmonic room below Nyquist. Its harmonic limit must fit that note, leaving unused room at lower notes.
>
> **Where it stops:** Playback interpolation and modulation can create additional spectral error; counting stored harmonics is only part of validation.

## Key takeaways

- Keep harmonics strictly below Nyquist; exclude exact equality under this policy.
- Additive generation trades processing work for explicit spectral control; tables trade memory for playback cost.

## Further reading

- [Alias-free classic waveforms — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Additive synthesis — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Additive_Synthesis.html)
