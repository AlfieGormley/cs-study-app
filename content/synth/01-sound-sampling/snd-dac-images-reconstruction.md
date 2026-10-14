---
id: snd-dac-images-reconstruction
title: DAC images and reconstruction filters
level: intermediate
minutes: 3
summary: Distinguish out-of-band DAC images from in-band aliases and trace the conversion chain.
sourceLesson: snd-aliasing
---

## Reconstruction: the DAC side

A DAC is given one number per sample period. A crude converter holds each value until the next (a **zero-order hold**), producing a staircase. That staircase contains the wanted signal plus **image frequencies**: copies of the spectrum mirrored around every multiple of the sample rate.

```formula
f_img = m × fs ± f
f_img = 1 × 48 − 1 = 47 kHz
f_img = 1 × 48 + 1 = 49 kHz
where
f_img: the frequency of an image component, in kilohertz (kHz) here
m: a whole number 1, 2, 3, …, picking which multiple of the sample rate the image sits around
fs: the sample rate; here 48 kHz
f: the frequency of the wanted tone; here 1 kHz
±: plus or minus: each multiple gives two images, one below it and one above
kHz: kilohertz, thousands of cycles per second
In words: a 1 kHz tone played at 48 kHz also produces images at 47 and 49 kHz, then 95 and 97 kHz, and so on.
```

Images are not aliases. An alias is a wrong frequency *inside* the audio band, created when sampling; images sit *above* Nyquist, created when converting back to analogue, and a filter can remove them.

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
