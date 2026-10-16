---
id: syn-bandlimited-additive-tables
title: Harmonic limits and wavetable ranges
level: intermediate
minutes: 4
summary: Harmonic limits and wavetable ranges.
sourceLesson: syn-bandlimited
---

## Established fixes

There is no free lunch. Each method trades CPU, memory, latency or flexibility.

### 1. Additive synthesis

Sum only the harmonics below Nyquist. How many is that? The largest whole number whose harmonic stays strictly below half the sample rate:

```formula
H = ⌈(f_s / 2) / f_0⌉ − 1
H = ⌈24000 / 1245⌉ − 1 = ⌈19.3⌉ − 1 = 19
H = ⌈24000 / 50⌉ − 1 = 480 − 1 = 479
where
H: the number of harmonics that fit below Nyquist (the highest usable harmonic number)
⌈x⌉: the ceiling of x: x rounded up to the next whole number; a whole number stays as it is
f_s: the sample rate, here 48,000 Hz
f_s / 2: the Nyquist frequency, here 24,000 Hz
f_0: the note's fundamental frequency, in hertz (Hz)
In words: divide Nyquist by the note's frequency, round up, and subtract one, so that a harmonic landing exactly on Nyquist is excluded.
```

For this note that is harmonics 1 to 19. The result is perfectly band-limited by construction. The cost is one sine per harmonic per sample: a 50 Hz note at 48 kHz has 479 harmonics below Nyquist. Fine offline, expensive for a polyphonic synth on a microcontroller.

### 2. Band-limited wavetables (mipmaps)

Precompute single-cycle tables using additive synthesis, offline. Keep several versions: one per octave (say), each containing only the harmonics that stay below Nyquist for the **highest** note that table will play. At playback, choose the table for the current pitch and read it with a phase accumulator and interpolation. The same counting rule sets each table's harmonic limit, using the highest note the table serves:

```formula
H = ⌈(f_s / 2) / f_top⌉ − 1
f_top = 2000 Hz: ⌈24000 / 2000⌉ − 1 = 11
f_top = 1000 Hz: ⌈24000 / 1000⌉ − 1 = 23
f_top = 500 Hz: ⌈24000 / 500⌉ − 1 = 47
where
H: the highest harmonic the table may contain
⌈x⌉: the ceiling of x: rounded up to a whole number (a whole number stays as it is)
f_s: the sample rate, 48,000 Hz, so f_s / 2 = 24,000 Hz
f_top: the highest note the table will play, in hertz (Hz)
Hz: hertz, cycles per second
In words: each octave lower, the table can hold about twice as many harmonics.
```

This is cheap per sample and works for any waveform, which is why wavetable synths use it. The costs are memory, a slight loss of brightness at the bottom of each table's range, and possible audible switching between tables (crossfading helps). Some designs deliberately allow harmonics that fold back *above* 20 kHz, keeping more brightness at the cost of some inaudible aliasing.

## Key takeaways

- Count harmonics strictly below Nyquist, including exact equality with Nyquist.
- Additive generation trades processing work for explicit spectral control; tables trade memory for playback cost.

## Further reading

- [Alias-free classic waveforms — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
- [Additive synthesis — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Additive_Synthesis.html)
