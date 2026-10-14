---
id: snd-fft-bin-spacing
title: FFT bins and capture length
level: advanced
minutes: 3
summary: Calculate FFT bin frequencies and choose a capture long enough for the spacing you need.
sourceLesson: snd-measuring
---

## Read a spectrum with numpy's FFT

The **FFT** (fast Fourier transform) takes N samples and returns how much of each frequency they contain, at evenly spaced frequencies called **FFT bins**. For real input (ordinary audio), numpy's `rfft` returns the bins from 0 Hz up to the Nyquist frequency:

```formula
K = N / 2 + 1
Δf = fs / N
f_k = k × Δf
Δf = 48000 / 48000 = 1 Hz
where
K: the number of bins rfft returns (when N is even)
N: the number of samples analysed (the capture length)
fs: the sample rate, in samples per second
Δf: delta f, the bin spacing: the frequency gap between neighbouring bins, in hertz (Hz)
f_k: the frequency at the centre of bin number k, in hertz (Hz)
k: the bin index, 0, 1, 2, … up to N/2; bin 0 is 0 Hz (DC) and bin N/2 is the Nyquist frequency
Hz: hertz, cycles per second
In words: the bins are spaced by the sample rate divided by the number of samples, which is one over the capture's length in seconds. One second of audio gives 1 Hz bins.
```

Three facts you need to read it correctly:

1. **Bin spacing** is the sample rate divided by the number of samples. One second at 48 kHz gives 1 Hz bins; 0.1 s gives 10 Hz bins. Longer captures give finer frequency resolution.
2. **Scaling:** numpy's raw output grows with N. For ordinary positive-frequency bins, multiply by 2 and divide by the sum of the window (in the next unit). DC and the even-length Nyquist bin have no negative-frequency partner and are not doubled.
3. **Windowing:** multiply the capture by a smooth **window** (Hann is a good default) that tapers its ends to zero. Without it, a frequency that doesn't fit a whole number of cycles in the capture smears energy across the spectrum. That smearing is called **spectral leakage**.

Zero-padding a capture gives more displayed frequency points by interpolating the same transform. It adds no measured information and cannot replace a longer capture when separating nearby tones.

## Key takeaways

- For even-length real input, rfft returns half the sample count plus one bins.
- Bin spacing is sample rate divided by capture length in samples.
- Longer captures give finer bin spacing; windowing and correct scaling are also needed to read a spectrum.

## Further reading

- [numpy.fft.rfft — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html)
- [numpy.fft.rfftfreq — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html)
- [Zero padding and spectral interpolation — Julius O. Smith](https://www.dsprelated.com/freebooks/sasp/Zero_Padding_Time_Domain.html)
