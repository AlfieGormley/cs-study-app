---
id: ds-sampling-aliasing
title: When sampling hides frequency
level: basic
minutes: 3
summary: Recognise aliases and place anti-alias filtering before sampling.
---

Uniform samples can agree even when their underlying continuous waves differ. This ambiguity is **aliasing**. Once two possible inputs produce the same samples, analysing those samples alone cannot tell which input occurred. Sampling faster is useful only if it is fast enough for the signal content arriving at the sampler.

## Keep baseband content below half the rate

A **baseband** signal occupies frequencies from zero up to some highest frequency. A **band-limited** ideal signal has no content above that limit. The **Nyquist frequency** is half the sample rate. To preserve arbitrary phase at the upper edge of this baseband signal, its highest frequency must stay strictly below that boundary:

```formula essential
F_s > 2f_max
f_N = F_s / 2
where
F_s: sample rate, in samples per second
f_max: highest frequency present in the ideal baseband signal, in hertz (Hz)
f_N: Nyquist frequency, half the sample rate, in hertz (Hz)
Hz: hertz, cycles per second
In words: The sample rate must exceed twice the highest baseband frequency. Keeping the signal below half the sample rate prevents overlap in the ideal band-limited case; the endpoint is excluded here.
```

Why exclude the endpoint? A sine at exactly half the sample rate, with zero starting phase, is sampled at its zero crossings. Every sample is zero in exact arithmetic. A cosine at that same frequency alternates positive and negative values. Merely having two samples per cycle does not preserve every possible phase and amplitude at the boundary.

A finite record is also not the infinite sequence assumed by ideal reconstruction theory. The condition prevents spectral overlap for the ideal band-limited case; it does not promise recovery of arbitrary data from a few samples.

## An explicit fold

At 1000 samples per second, a 700 Hz cosine produces the same samples as a 300 Hz cosine, with equal amplitude and zero starting phase. The higher frequency appears below the 500 Hz Nyquist limit. If both tones arrive together, their stored contributions overlap: a later analysis cannot reliably assign the combined values back to the two original tones.

In this frequency interval the alias behaves like a reflection around half the sample rate. Higher frequencies can fold repeatedly, and phase can change during folding. The example specifies cosine and starting phase to avoid suggesting that every sine keeps its original sign.

> [!analogy] Real-world analogy: A wheel in a film
> A wheel turning quickly can appear to turn slowly or backwards in regularly spaced film frames.
>
> **How it maps:** The frames sample position. Different numbers of turns between frames can produce the same visible positions, just as different frequencies can produce the same samples.
>
> **Where it stops:** A real wheel has visual features and exposure blur. The DSP claim concerns mathematical sample values, not every detail of a video.

## Prevent the ambiguity before it happens

An analogue **anti-alias filter** reduces high-frequency content before an analogue-to-digital converter (ADC) takes samples. Real filters need a transition band, so leave room between wanted frequencies and the Nyquist limit. The filter reduces unwanted content to an acceptable level rather than forming an ideal brick-wall cutoff.

A digital filter after this sampling step cannot separate a wanted 300 Hz component from a 700 Hz component already folded onto it. When later reducing a digital sample rate, filtering must likewise precede the rate reduction.

## Key takeaways
- Different continuous frequencies can produce identical samples.
- Use a strict upper frequency margin and account for real anti-alias filter transitions.
- Filtering must act before the sampling operation that would cause the alias.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH3.PDF)
- [MIT 6.003: sampling theorem and aliasing](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/12e6e5d7567fca2e993ef8563fef5a60_MIT6_003F11_lec21.pdf)
