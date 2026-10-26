---
id: dp-dft-bins
title: What a Fourier bin measures
level: basic
minutes: 4
summary: Turn a finite sample record into frequency components and label its bins correctly.
---

A time plot shows when samples rise and fall. A **discrete Fourier transform**, or **DFT**, describes that same finite record as a combination of regularly spaced sinusoidal patterns. Each **frequency bin** tests one of those patterns across the whole record.

A strong match produces a large coefficient. Each coefficient is complex: its two parts preserve both magnitude and phase. The raw magnitude is not yet a calibrated tone amplitude. The **fast Fourier transform**, or **FFT**, is an efficient way to calculate these same DFT coefficients; it adds no observations.

## What a bin tells you

Imagine comparing the samples with a steady oscillation. At the matching rhythm, contributions reinforce each other. At many mismatched rhythms, positive and negative contributions cancel. The DFT does this with both cosine and sine components, so it can also describe where the oscillation is within its cycle.

> [!analogy] Real-world analogy: checking a rhythm
> Clap at a chosen steady rhythm while watching a repeating movement. A matching rhythm stays aligned; a mismatched rhythm drifts.
>
> **How it maps:** Each DFT bin tests one rhythm across the full record. Adding contributions reinforces a matching pattern and cancels many mismatched ones.
>
> **Where it stops:** A DFT uses signed and complex arithmetic to measure phase as well as strength; simply counting claps cannot reproduce it.

The transform describes the finite record exactly, within numerical error. It does not establish that a physical machine contains only the bin frequencies. A single tone between bins can produce several large coefficients. Do not count non-zero bins as separate physical oscillators.

## Label the frequency axis

The sample rate sets the physical time scale. The transform length sets how many frequency positions share that scale. With no padding, recording more samples at the same rate gives closer bin labels. Changing the sample rate without updating the labels gives the wrong frequency axis.

```formula essential
Δf = F_s / N
f_k = kΔf
where
Δf: spacing between neighbouring DFT bins, in hertz (Hz)
F_s: sample rate, in samples per second, expressed in Hz
N: number of acquired samples and transform points, with no zero padding
f_k: frequency of non-negative bin k, in Hz
k: non-negative integer bin index
Hz: hertz, cycles per second
In words: bin spacing is the sample rate divided by the unpadded record length; each non-negative bin is another step along that grid.
```

Eight samples taken at 800 samples per second give non-negative labels of 0, 100, 200, 300 and 400 Hz. These labels exist even when a bin's coefficient is zero.

## Choose the transform for the input

For real input, the negative-frequency coefficients are complex conjugates of the positive-frequency coefficients: they carry redundant information. NumPy's `rfft` keeps the non-negative half. Interior coefficients can still be complex even though the samples are real.

An even-length real record includes DC and an exact Nyquist endpoint; an odd-length record has no bin exactly at Nyquist. For arbitrary complex input, negative frequencies can hold independent information, so use the full `fft`.

Use matching frequency-label functions. `rfftfreq` labels the real-input output; `fftfreq` labels the full output in stored order: zero, positive frequencies, then negative frequencies. For an even length, the full transform labels its Nyquist slot negative while the real-input transform labels it positive. Both describe the same sampled endpoint.

## Key takeaways

- A bin measures a pattern across a finite record; it is not proof of a separate physical tone.
- An FFT calculates a DFT efficiently, with no extra information.
- Match the frequency axis to the sample rate, transform length and real or complex input.

## Further reading

- [NumPy: DFT definitions and conventions](https://numpy.org/doc/stable/reference/routines.fft.html)
- [NumPy: real-input FFT](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [NumPy: real-input frequency labels](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html)
