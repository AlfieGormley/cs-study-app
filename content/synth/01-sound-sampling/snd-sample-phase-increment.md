---
id: snd-sample-phase-increment
title: Samples per cycle and phase increment
level: basic
minutes: 3
summary: Predict how pitch and sample rate change samples per cycle and per-sample phase advance.
sourceLesson: snd-waves
---

## From time to samples

A digital synth computes values only at evenly spaced sample instants. The **sample rate** says how many of these occur each second; 48,000 per second is a common rate.

Each sample uses the sine’s value at that instant. The first sample is at the start, the next is one sample period later, and so on; samples need not land on peaks or whole-cycle boundaries.

Two practical quantities describe how an oscillator moves through those instants.

**Samples per period** tells you how many numbers describe one cycle:

```formula reference
S = fs / f
where
S: the number of samples in one cycle (samples per period); not usually a whole number
fs: the sample rate, in samples per second; here 48,000
f: the frequency of the tone, in hertz (Hz), cycles per second; here 440
In words: divide samples per second by cycles per second to get samples per cycle. A 440 Hz cycle at 48 kHz spans about 109 samples.
```

**Phase increment** is how far round the cycle you move between one sample and the next. It's the reciprocal of samples per period:

```formula reference
Δp = f / fs
Δθ = 2πΔp
where
Δp: delta p, the phase increment in cycles per sample (the Greek letter Δ, delta, means "a step in")
Δθ: delta theta, the same increment measured in radians per sample
f: the frequency of the tone, in hertz (Hz)
fs: the sample rate, in samples per second
π: pi, about 3.14159
cycles: fractions of one full cycle
rad: radians; one full cycle is 2π radians
In words: Higher frequency advances phase further at each sample; a higher sample rate needs smaller steps for the same pitch. Convert a cycle step to radians by multiplying by two pi.
```

At 48 kHz, a 440 Hz cycle spans about 109 sample periods, while a 3520 Hz cycle spans fewer than 14. Those spans need not be whole numbers.

Notice:

- Samples per period is rarely a whole number. A 440 Hz cycle at 48 kHz takes 109.09 samples, so the samples land at slightly different points of each cycle. That's fine; the phase is tracked as a real number.
- Higher pitches get **fewer** samples per cycle. At 3520 Hz you have under 14 points per cycle. The Nyquist-limit unit shows where this runs out.
- The phase increment depends on **both** tone frequency and sample rate. Change the rate to 44.1 kHz and the step for every note changes. If a synth assumes the wrong sample rate, every note comes out at the wrong pitch.

## Pitfalls

- **Hard-coding the sample rate.** Compute the increment from the actual rate the audio hardware is running at.

## Key takeaways

- Sample time is the sample index divided by the sample rate.
- Samples per period is sample rate divided by tone frequency; it need not be a whole number.
- Phase increment is tone frequency divided by sample rate in cycles per sample. Use the hardware’s actual rate.

## Further reading

- [Sinusoids — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sinusoids.html)
- [Numerically controlled oscillator (phase accumulator) — Wikipedia](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
