---
id: dp-time-frequency
title: Following frequencies through time
level: intermediate
minutes: 4
summary: Build a short-time spectrum and distinguish frame duration, hop spacing and frequency-grid spacing.
---

A single FFT describes everything in its record together. If a machine first vibrates at one frequency and later another, that spectrum does not show their order. A **short-time Fourier transform**, or **STFT**, instead analyses successive short, windowed records called **analysis frames**.

A **spectrogram** displays a squared-magnitude or power-related version of those transforms: time on one axis, frequency on another and strength shown by colour. Check what the colours mean. A coloured plot is not automatically a calibrated PSD.

## Frame length controls what gets blended

Each frame observes a span of time. A longer frame gives narrower spectral features for steady tones, making close frequencies easier to distinguish under suitable conditions. It also combines events across a longer interval. If a tone changes inside the frame, both its earlier and later frequencies can contribute to that frame.

A shorter frame localises changes more closely in time, but broadens its frequency features. Choose the frame length for the event you want to understand rather than assuming a more detailed-looking plot has resolved everything.

## Hop controls how often you look

The **hop** is the distance in samples between neighbouring frame starts. A hop shorter than the frame length makes the frames overlap. Reducing the hop gives more frequent spectra by sharing more samples. It does not shorten each frame's observation or remove its time-frequency trade-off.

For example, a frame can observe 125 milliseconds while another frame starts every 31.25 milliseconds. The frequent updates still each mix information over a 125-millisecond span.

```formula reference
T_w = L / F_s
T_h = H / F_s
where
T_w: duration observed by each frame, in seconds
T_h: interval between consecutive frame starts, in seconds
L: number of acquired samples per frame
H: hop length, in samples
F_s: sample rate, in samples per second
In words: frame duration is the frame's sample count divided by the sample rate; update spacing uses the hop count instead, so more overlap gives more updates without shortening the observation.
```

> [!analogy] Real-world analogy: overlapping snapshots
> Take long-exposure photographs at frequent intervals. Starting another exposure sooner creates more photographs, but each photograph still blends movement over its own exposure.
>
> **How it maps:** Frame length is the observation span and hop is the interval between observations. Overlapping frames share samples.
>
> **Where it stops:** The STFT measures oscillation components using a window, rather than brightness. A smaller hop cannot improve the window's intrinsic frequency discrimination.

## Read a spectrogram's contract

Before comparing two plots, establish the window and frame length, hop, FFT length, time labels and boundary policy. Extra zero padding gives more frequency-grid positions inside each frame; it does not lengthen the acquired frame.

Some implementations label frames by their centres, others by their starts. Some extend the signal at the edges, while others omit incomplete frames. A centred window near an edge can include assumed samples outside the actual record. These choices affect apparent event timing and edge content.

Finally match the strength normalisation and colour units. Amplitude, squared magnitude and PSD use different normalisations. SciPy's `ShortTimeFFT` exposes frame, hop and scaling choices; record the settings with the plot so another reader can interpret it.

## Key takeaways

- An STFT follows changing spectra using successive windowed frames.
- Frame length controls the observation span; hop controls update spacing.
- Match time labels, boundaries and scaling before comparing spectrograms.

## Further reading

- [SciPy: short-time Fourier transform](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html)
- [SciPy: ShortTimeFFT](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html)
