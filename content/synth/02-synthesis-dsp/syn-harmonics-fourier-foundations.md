---
id: syn-harmonics-fourier-foundations
title: Periodic sounds as Fourier series
level: intermediate
minutes: 3
summary: Periodic sounds as Fourier series.
sourceLesson: syn-harmonics
---

Play a sine, a triangle, a square and a sawtooth at the same pitch and loudness. Each sounds clearly different: the sine pure, the triangle soft, the square hollow, the saw buzzy and bright. Pitch and loudness are equal, so the difference is **timbre**, and for steady periodic tones timbre is largely set by the **spectrum**: which frequencies are present, and how strong each one is.

This lesson gives you the spectra of the standard waveforms and a way to verify them. Every later block (band-limiting, filters) is easier to reason about in these terms.

## Fourier series for ordinary periodic audio signals

A nonconstant periodic waveform has a fundamental frequency of one divided by its shortest repeating period, and, under the usual Fourier-series conditions for piecewise-smooth signals, it can be represented by a mean plus sinusoidal components at whole-number multiples of that repeat rate. At an ideal jump the series takes the midpoint of the one-sided limits:

```formula
f_0 = 1 / T
x(t) = DC + Σ A_n sin(2πn f_0 t + φ_n)
where
f_0: the fundamental frequency, in hertz (Hz): how many times per second the waveform repeats
T: the period, the time one repeat takes, in seconds (s)
x(t): the value of the waveform at time t
t: time, in seconds (s)
DC: the waveform's mean (average) value, a constant offset; zero for the centred waveforms here
Σ: sigma, "sum of": add up the term after it for n = 1, 2, 3 and so on (in principle for ever)
n: the harmonic number, a whole number 1, 2, 3...; component n has frequency n × f_0
A_n: the amplitude (peak height) of component n
sin: the sine function, taking an angle in radians
π: pi, about 3.14159; 2π radians is one full cycle
φ_n: phi n, the phase of component n: where in its cycle that sine starts, in radians
·: multiplication, the same as ×
Hz: hertz, cycles per second
s: seconds
In words: any repeating wave equals its average plus a stack of sines at 1, 2, 3... times the repeat rate, each with its own height and starting point.
```

For example, a wave repeating every 10 milliseconds has a 100 Hz repeat rate. Its non-DC components lie on the 100, 200, 300 Hz grid and so on; some may have zero amplitude.

- DC is the mean value (zero for the centred waveforms here).
- The first harmonic is the **fundamental**; perceived pitch need not equal the strongest component.
- The second and higher harmonics are the **overtones**. “Harmonic” also includes the fundamental, so these words are not identical labels.
- Every component has its own amplitude and phase.

This is the **Fourier series**. Intuitively: a single sinusoid has one non-zero positive-frequency component, while a more complicated periodic waveform requires more components (and possibly a DC mean). The sharper the features of a waveform (corners, jumps), the more high harmonics it needs to build them.

The *magnitudes* A_n plotted against frequency form the **magnitude spectrum**: a row of spikes at multiples of `f0`, each with a height.

## Key takeaways

- A periodic sound can be decomposed into a mean plus harmonics with individual phases and magnitudes.
- Its repeat rate sets the harmonic grid; the strongest component need not be the perceived pitch.

## Further reading

- [Fourier series — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Fourier_Series_FS_Relation.html)
- [Gibbs phenomenon — NIST DLMF](https://dlmf.nist.gov/6.16)
