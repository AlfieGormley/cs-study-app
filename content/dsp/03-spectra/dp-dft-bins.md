---
id: dp-dft-bins
title: What a Fourier bin measures
level: basic
minutes: 5
summary: Turn a finite sample record into frequency components and label its bins correctly.
---

A time plot shows when samples rise and fall. A **discrete Fourier transform**, or **DFT**, describes the same finite record using regularly spaced sinusoidal components. Each **frequency bin** stores a complex coefficient: two numbers that preserve both magnitude and phase. A large magnitude means a strong match to that bin's rotating pattern; raw magnitude is not yet a calibrated tone amplitude.

The **fast Fourier transform**, or **FFT**, is an efficient algorithm for calculating a DFT. It does not create a different kind of spectrum. NumPy's default forward transform uses the following unnormalised sum.

## A finite sum, not a calculus prerequisite

For each bin, multiply each input sample by a rotating complex number, then add all those contributions. The cosine gives its real component and the negative sine its imaginary component.

```formula
θ = (2πkn) / N
X[k] = Σ x[n](cos(θ) − j sin(θ))
where
θ: rotation angle for the current sample and bin, in radians
π: pi, approximately 3.14159
k: integer frequency-bin index, from 0 through N − 1
n: integer sample index, from 0 through N − 1
N: number of input samples and DFT bins, a positive integer
X[k]: complex coefficient at bin k; with this unnormalised sum its numerical scale grows with N, in the input sample's units
Σ: add the displayed term once for every n from 0 through N − 1, keeping k fixed
x[n]: input sample at index n, in the signal's units
cos: cosine function, accepting an angle in radians and returning a unitless real number
sin: sine function, accepting an angle in radians and returning a unitless real number
j: imaginary unit, whose square is −1; it distinguishes the imaginary component
In words: each bin measures how well the whole record matches one particular rotating pattern.
```

This is a representation of a finite record. It does not prove that an observed machine or sensor contains only these exact frequencies. A tone between bins can contribute to many bins.

> [!analogy] Real-world analogy: checking a rhythm
> Tap at a chosen steady rhythm while watching a repeating movement. A matching rhythm stays aligned; a mismatched rhythm drifts.
>
> **How it maps:** Each DFT bin tests one rhythm across the full record. Adding contributions reinforces a matching pattern and cancels many mismatched ones.
>
> **Where it stops:** A DFT uses signed and complex arithmetic to measure phase as well as strength; simply counting taps cannot reproduce it.

## Label the frequency axis

For the non-negative bins, the physical frequency depends on both the sample rate and the record length.

```formula
Δf = F_s / N
f_k = kΔf
Δf = 800 Hz / 8 = 100 Hz
where
Δf: spacing between adjacent DFT bins, in hertz (Hz)
F_s: sample rate, here 800 samples per second, expressed in Hz
N: record length, here 8 samples
f_k: frequency of non-negative bin k, in Hz
k: non-negative bin index; for this even-length real record, 0 through N / 2
Hz: hertz, cycles per second
In words: eight samples at 800 samples per second produce non-negative bin labels 0, 100, 200, 300 and 400 hertz.
```

For real input, negative-frequency coefficients are complex conjugates of the corresponding positive-frequency coefficients. This redundancy lets `np.fft.rfft` return only the non-negative half. For eight samples it returns five coefficients, including DC and the 400 Hz Nyquist endpoint. An odd-length real record has no bin exactly at Nyquist.

For arbitrary complex input, use `np.fft.fft`: its negative frequencies can contain independent information. `np.fft.fftfreq` labels the full output in its stored order: zero, positive frequencies, then negative frequencies. For even lengths it labels the Nyquist slot as negative; `rfftfreq` labels that endpoint positive. These are representations of the same sampled endpoint.

## Complete Python example

`np.arange` creates the integer indices. NumPy's cosine operates element by element; `rfftfreq` takes the sample interval in seconds. Values here are dimensionless.

```python
import numpy as np

n = np.arange(8)
x = np.cos(2 * np.pi * n / 8)
f = np.fft.rfftfreq(8, d=1 / 800)
X = np.fft.rfft(x)
print(f.tolist())
print(np.round(abs(X), 6).tolist())
# Bin 1 has raw magnitude 4, not 1.
```

The outputs are `[0.0, 100.0, 200.0, 300.0, 400.0]` and `[0.0, 4.0, 0.0, 0.0, 0.0]`, allowing tiny floating-point errors. The next lesson converts that raw 4 into the cosine's peak amplitude of 1.

## Key takeaways

- A DFT represents a whole finite record; an FFT computes that transform efficiently.
- A bin contains a complex coefficient, not just a frequency label.
- Use the sample rate and transform length to label bins, and use the real-input transform only for real input.

## Further reading

- [NumPy: DFT definitions, conventions and frequency order](https://numpy.org/doc/stable/reference/routines.fft.html)
- [NumPy: real-input FFT](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [NumPy: real-input frequency labels](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html)
