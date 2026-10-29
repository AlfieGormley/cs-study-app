---
id: syn-synthesis-overview-fm-pm
title: FM, PM and sidebands
level: basic
minutes: 3
summary: FM, PM and sidebands.
sourceLesson: syn-synthesis-overview
---

### FM and PM

In **frequency modulation** one signal varies an oscillator’s instantaneous frequency. Here we consider sinusoidal modulation of one sine oscillator (the *carrier*) by another (the *modulator*), at constant rates and depth. More general modulation need not have this same simple sideband grid. This creates new frequency components, called **sidebands**, at the carrier frequency plus and minus multiples of the modulator frequency, so two sine oscillators can produce a complex spectrum. The optional relationship records that spacing:

```formula reference
f_sb = f_car ± k f_mod
where
f_sb: the frequency of one sideband, in hertz (Hz)
f_car: the carrier frequency (the oscillator you hear), in Hz
f_mod: the modulator frequency (the oscillator doing the modulating), in Hz
k: a whole number, 1, 2, 3 and so on; each value gives one pair of sidebands
±: "plus or minus": each k gives one sideband above the carrier and one below it
Hz: hertz, cycles per second
In words: sidebands sit either side of the carrier, spaced at whole multiples of the modulator frequency.
```

For example, a 400 Hz carrier modulated by a 100 Hz modulator gives sidebands at 300 and 500 Hz (the first pair), 200 and 600 Hz (the second pair), and so on, so the possible components lie on a 100 Hz harmonic grid. Which are audible depends on their levels and cancellation; perceived pitch is not guaranteed to be 100 Hz. A ratio such as 400 Hz to 141 Hz does not give a simple low-order harmonic relationship and can sound metallic. Since those two integer frequencies do share a 1 Hz divisor, it would be wrong to claim they have no common mathematical fundamental. How strong each pair is depends on the **modulation index** (how hard the modulator pushes); a low non-zero index concentrates most energy in the carrier and first pairs, while a high index usually spreads significant energy over more pairs. More distant sideband terms are generally small rather than exactly absent, and individual terms can have zeros. (A sideband that would land below 0 Hz reflects back to a positive frequency.)

John Chowning developed FM synthesis at Stanford from 1967 and Yamaha licensed it; the DX7 (1983) made it famous.

Yamaha's commercial "FM" (the DX7 included) is actually implemented as **phase modulation** (adding the modulator to the carrier's *phase* rather than its frequency). The two are mathematically closely related: phase-modulating with a signal is the same as frequency-modulating with its derivative, after converting phase units to frequency units. A practical advantage of PM is that a modulator with a DC offset only shifts the carrier's phase, whereas in true FM it shifts the carrier's pitch. A small FM/PM oscillator network can create rich spectra with little work, but cost grows with its operators, oversampling and implementation. Predicting a patch by ear can be difficult because sideband levels change nonlinearly with index.

## Key takeaways

- Audio-rate frequency or phase modulation produces sidebands.
- The modulation index controls their distribution, not just the carrier/modulator ratio.

## Further reading

- [Sinusoidal FM and PM — Julius O. Smith](https://ccrma.stanford.edu/~jos/mdft/Sinusoidal_Frequency_Modulation_FM.html)
- [Frequency modulation synthesis — CMU](https://www.cs.cmu.edu/~music/icm-online/readings/fm-synthesis/index.html)
- [History of FM synthesis — Yamaha](https://hub.yamaha.com/keyboards/synthesizers/history-of-the-synthesizer-part-2/)
