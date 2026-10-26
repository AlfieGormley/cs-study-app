---
id: snd-dac-images-reconstruction
title: DAC images and reconstruction filters
level: intermediate
minutes: 3
summary: Distinguish out-of-band DAC images from in-band aliases and trace the conversion chain.
sourceLesson: snd-aliasing
---

## Reconstruction: the DAC side

A DAC is given one number per sample period. A crude converter holds each value until the next (a **zero-order hold**), producing a staircase. That staircase contains the wanted signal plus **image frequencies**: copies of the spectrum mirrored around multiples of the sample rate.

For a 1 kHz tone at a 48 kHz sample rate, the first images sit at 47 and 49 kHz: one kilohertz either side of the sample rate. More sit at 95 and 97 kHz, either side of twice the rate.

Images are not aliases. An alias is a folded component *inside* the represented band, created when sampling; images sit *above* Nyquist, created when converting back to analogue, and a filter can remove them.

A **reconstruction filter** (anti-imaging filter) removes the images, leaving the smooth wave the theorem promises. Most modern audio converters are **delta-sigma** designs that internally oversample and do much of this filtering digitally, so their external analogue filtering can be simple. Follow the converter or codec datasheet's recommended output circuit.

```flow
Analogue in
Anti-aliasing low-pass filter
ADC samples at the sample rate
Digital processing below Nyquist
DAC outputs samples
Reconstruction low-pass filter
Analogue out
```

## Key takeaways

- Holding samples creates image frequencies around multiples of the sample rate.
- Reconstruction filtering removes images; it cannot undo aliases already in the samples.
- Modern converters combine internal digital filtering with their specified analogue circuits.

## Further reading

- [Sampling Theorem — Julius O. Smith, Mathematics of the DFT (CCRMA)](https://ccrma.stanford.edu/~jos/mdft/Sampling_Theorem.html)
- [Reconstruction filter — Wikipedia](https://en.wikipedia.org/wiki/Reconstruction_filter)
- [PCM5102A audio DAC datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf)
