---
id: dp-zero-padding
title: More bins do not mean more observation
level: intermediate
minutes: 4
summary: Use zero padding to sample a spectrum more finely without mistaking it for new resolving power.
---

**Zero padding** appends zeros to an acquired record before its FFT. The longer transform evaluates the same finite-record spectrum at more closely spaced frequencies. A plotted peak looks smoother and a grid-based peak search can land closer to its true location. No new measurements have been made.

The important distinction is between the spacing of the displayed frequency grid and the ability to distinguish neighbouring tones. Both are sometimes called **frequency resolution**, so say which you mean.

## Keep observation and transform length separate

The acquired sample count and sample rate determine how long you observed the signal. The FFT length includes any appended zeros and determines the grid spacing. Padding changes the second length while leaving the first unchanged.

For example, acquire 64 samples at 640 samples per second: a tenth-second record. Its unpadded bins are 10 Hz apart. Pad it to 256 points and the grid becomes 2.5 Hz apart, but the acquired observation remains a tenth of a second.

```formula reference
T = N / F_s
Δf = F_s / M
where
T: acquired record duration, in seconds, using N sample intervals
N: acquired sample count
F_s: sample rate, in samples per second, expressed in hertz
M: FFT length, including appended zeros, at least N
Δf: displayed frequency-grid spacing, in hertz
In words: acquired duration comes from the real sample count and sample rate; displayed bin spacing comes from the sample rate and the FFT length, including padding.
```

> [!analogy] Real-world analogy: enlarging a photograph
> Enlarging an existing photograph can make its shapes easier to inspect. It does not capture details that the camera never recorded.
>
> **How it maps:** Extra FFT points sample the existing finite-record spectrum more densely; extra acquired samples can supply new observation information.
>
> **Where it stops:** Zero padding is exact evaluation on a denser frequency grid, not a camera's pixel interpolation algorithm. Its usefulness and limitations follow from the record's transform.

## Choose the change that solves the problem

If a peak falls between coarse grid points, padding can improve the display and the search grid. For a 73 Hz cosine in the example above, the largest unpadded bin is labelled 70 Hz and the padded one 72.5 Hz. The closer label does not establish exact frequency or measurement uncertainty: leakage, noise, the finite record and other tones can bias the estimate.

If two tones blend into one broad feature, padding alone cannot narrow the window's main lobe in hertz. Collect a longer record if the tones stay steady long enough. That can narrow the spectral features, but window shape, relative tone levels and noise still govern whether the tones can be separated. A longer observation can also mix changes that happen during it.

## Preserve amplitude calibration

Appending zeros should not make the same tone physically smaller. For coherent-tone calibration, retain the original acquired sample count when there was no taper, or the original window-weight sum when there was a taper. Dividing by the longer padded length would falsely reduce amplitude. Keep that calibration issue separate from off-bin peak error.

## Key takeaways

- Padding gives a denser grid without a longer observation.
- More acquired time can narrow spectral features when the signal remains steady; padding cannot.
- A peak's grid label is an estimate, and padding must not change coherent-tone amplitude scaling.

## Further reading

- [NumPy: FFT length and zero padding](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [Steven W. Smith: Fourier transform properties](https://www.dspguide.com/CH10.PDF)
