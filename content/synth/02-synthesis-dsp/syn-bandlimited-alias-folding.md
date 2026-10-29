---
id: syn-bandlimited-alias-folding
title: Where naive oscillator harmonics fold
level: intermediate
minutes: 3
summary: Where naive oscillator harmonics fold.
sourceLesson: syn-bandlimited
---

The earlier harmonic-pattern unit showed that a sawtooth has harmonics at every multiple of its fundamental, forever. A digital system can only represent frequencies below half its sample rate (the **Nyquist frequency**: 24 kHz at a 48 kHz sample rate). Module 1 covered what happens to anything above: it **aliases**, folding back to a different frequency.

The naive oscillator from the oscillator units, `2.0 * p - 1.0`, samples an ideal saw directly. It therefore contains all those impossible harmonics, and they fold back into the audible band. This lesson explains how those folded components differ from ordinary brightness; the following units compare ways to prevent or reduce them.

## Where the harmonics go

Take a high-ish note: 1245 Hz (close to D#6) at a 48 kHz sample rate. Nyquist is 24 kHz, so harmonics 1 to 19 (up to 23,655 Hz) are fine. Harmonic 20 is at 24,900 Hz and folds back. A component above Nyquist lands at its distance from the nearest whole multiple of the sample rate:

```formula reference
f_h = h f_0
f_a = |f_h − k f_s|
where
f_h: the frequency of harmonic h, in hertz (Hz)
h: the harmonic number, 1, 2, 3...
f_0: the fundamental frequency (the note), here 1245 Hz
f_a: the alias: the frequency the harmonic actually appears at after sampling, in Hz
|x|: absolute value: x without its sign, so a distance is never negative
k: the whole number that makes k × f_s as close as possible to f_h (here k = 1, since all these harmonics lie between 24 and 72 kHz)
f_s: the sample rate, here 48,000 Hz
Hz: hertz, cycles per second
In words: sampling cannot tell a frequency apart from one that is a whole multiple of the sample rate away, so each harmonic above Nyquist shows up at its distance from the nearest multiple of the sample rate.
```

The table tracks each isolated ideal source harmonic using its reciprocal-harmonic-number amplitude. Several harmonics can fold to one sampled frequency and add or cancel, so these levels are not guaranteed total FFT-bin amplitudes.

A saw’s higher source harmonics get progressively weaker. Its 31st harmonic is about 30 dB below the ideal fundamental before sampling; that does not make its folded contribution harmless or uniquely determine the combined sampled-bin level.

| Harmonic | Lands at | Level (the reciprocal of harmonic number) |
|---|---|---|
| 20 | 23,100 Hz | −26.0 dB |
| 31 | 9,405 Hz | −29.8 dB |
| 38 | 690 Hz | −31.6 dB |
| 39 | 555 Hz | −31.8 dB |

Two things make this bad:

- **These aliases are not harmonic.** 9,405 Hz and 690 Hz are not multiples of 1245 Hz, so they sound like dissonant, metallic tones rather than brightness.
- **They move the wrong way.** Bend the pitch up and a real harmonic rises, but a folded one can *fall*. Pitch sweeps produce the tell-tale "birdie" whistles moving against the note.

A component 30 dB below the fundamental can be audible when it is poorly masked, but audibility depends on the sound, listener and playback level; that number alone is not an audibility threshold. Low notes suffer less, because their harmonics are already weak (the reciprocal of harmonic number is small) by the time they reach Nyquist.

> [!note] Why square waves are no better
> The naive square also has slowly decaying odd harmonics, so it can alias strongly. The exact folded levels differ from a saw. A naive triangle is much better (the reciprocal of harmonic number squared falls faster), and a fixed sine strictly below Nyquist has no upper harmonics to fold. Pitch modulation, clipping or an above-Nyquist sine requires separate analysis. The problem is **discontinuities**: a periodic jump requires harmonics extending to arbitrarily high frequencies.

## Key takeaways

- Naive sharp waveforms contain harmonics beyond Nyquist.
- Folded components can be inharmonic and move down while pitch moves up.

## Further reading

- [Aliasing — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Aliasing_Sampled_Signals.html)
- [Alias-free classic waveforms — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/blit.pdf)
