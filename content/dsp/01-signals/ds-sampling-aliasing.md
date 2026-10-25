---
id: ds-sampling-aliasing
title: When sampling hides frequency
level: basic
minutes: 5
summary: Recognise aliases and place anti-alias filtering before sampling.
---

Uniform samples can agree even when their underlying continuous waves differ. This ambiguity is **aliasing**. Once two possible inputs produce the same samples, analysing those samples alone cannot tell which input occurred. Sampling faster is useful only if it is fast enough for the signal content arriving at the sampler.

## Keep baseband content below half the rate

A **baseband** signal contains frequencies from zero up to some highest frequency. A **band-limited** ideal signal has no content above that limit. For arbitrary phase at the upper edge, use a strict inequality in the ideal sampling condition:

```formula
F_s > 2f_max
f_N = F_s / 2
where
F_s: sample rate, in samples per second
f_max: highest frequency present in the ideal baseband signal, in hertz (Hz)
f_N: Nyquist frequency, half the sample rate, in hertz (Hz)
Hz: hertz, cycles per second
In words: The sample rate must exceed twice the highest baseband frequency; the endpoint is excluded here.
```

Why exclude the endpoint? A sine at exactly half the sample rate, with zero starting phase, is sampled at its zero crossings. Every sample is zero in exact arithmetic. A cosine at that same frequency alternates positive and negative values. Merely having two samples per cycle does not preserve every possible phase and amplitude at the boundary.

A finite record is also not the infinite sequence assumed by ideal reconstruction theory. The condition prevents spectral overlap for the ideal band-limited case; it does not promise recovery of arbitrary data from a few samples.

## An explicit fold

At 1000 samples per second, a 700 Hz cosine produces the same samples as a 300 Hz cosine, with equal amplitude and zero starting phase. The higher frequency appears below the 500 Hz Nyquist limit. For this particular frequency range:

```formula
f_a = F_s − f
f_a = 1000 Hz − 700 Hz = 300 Hz
where
f_a: folded alias frequency, in hertz (Hz), for an input between half the sample rate and the sample rate
F_s: sample rate, numerically expressed in hertz here
f: input cosine frequency, in hertz (Hz)
Hz: hertz, cycles per second
In words: In this interval, reflect the input frequency around half the sample rate.
```

This is not a universal subtraction rule for all frequencies. Frequencies above one whole sample rate can fold repeatedly. Sine waves can also acquire a sign reversal during folding; specifying cosine and phase makes the example unambiguous.

> [!analogy] Real-world analogy: A wheel in a film
> A wheel turning quickly can appear to turn slowly or backwards in regularly spaced film frames.
>
> **How it maps:** The frames sample position. Different numbers of turns between frames can produce the same visible positions, just as different frequencies can produce the same samples.
>
> **Where it stops:** A real wheel has visual features and exposure blur. The DSP claim concerns mathematical sample values, not every detail of a video.

## Prevent the ambiguity before it happens

An analogue **anti-alias filter** reduces high-frequency content before an analogue-to-digital converter (ADC) takes samples. Real filters need a transition band, so leave room between wanted frequencies and the Nyquist limit. The filter reduces unwanted content to an acceptable level rather than forming an ideal brick-wall cutoff.

A digital filter after this sampling step cannot separate a wanted 300 Hz component from a 700 Hz component already folded onto it. When later reducing a digital sample rate, filtering must likewise precede the rate reduction.

This complete example checks the two cosines at sixteen sample instants. The small tolerance allows for floating-point round-off.

```python
import math
fs = 1000.0
lo = [math.cos(2 * math.pi * 300 * n / fs)
      for n in range(16)]
hi = [math.cos(2 * math.pi * 700 * n / fs)
      for n in range(16)]
print(max(abs(a-b) for a,b in zip(lo,hi))
      < 1e-12)
# True: samples alone cannot choose a tone
```

## Key takeaways
- Different continuous frequencies can produce identical samples.
- Use a strict upper frequency margin and account for real anti-alias filter transitions.
- Filtering must act before the sampling operation that would cause the alias.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH3.PDF)
- [MIT 6.003: sampling theorem and aliasing](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/12e6e5d7567fca2e993ef8563fef5a60_MIT6_003F11_lec21.pdf)
