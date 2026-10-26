---
id: dp-window-leakage
title: Finite records and spectral leakage
level: intermediate
minutes: 4
summary: Choose a named window, understand its trade-offs and correct coherent tone amplitude.
---

A noiseless single tone can produce many non-zero FFT bins. The transform describes a finite record as a repeating pattern. If the tone does not complete a whole number of cycles, joining repeated copies can create an abrupt boundary. Several bin patterns are needed to represent that record: **spectral leakage**.

This does not mean the FFT created sensor noise or discovered a separate oscillator at every bin. It means the finite observation affects the spectrum you can measure.

## A window changes the leakage pattern

An unweighted record uses a **rectangular window**. A **spectral window** multiplies the samples by a chosen set of weights before transforming. A taper gives less weight to the ends, reducing the effect of the repeated boundary.

The central feature around a tone is its **main lobe**; smaller surrounding features are **side lobes**. Compared with a rectangular window, a Hann window lowers side lobes but widens the main lobe. A weak tone far from a strong one can become easier to see, while two close tones can become harder to separate. Choose according to the distinction the measurement needs.

> [!analogy] Real-world analogy: a photograph's soft edge
> A hard-edged cut-out draws attention to its boundary. Fading the edge makes that boundary less abrupt, but blurs where it ends.
>
> **How it maps:** A taper reduces abrupt record boundaries and distant spectral leakage, while broadening a tone's central spectral feature.
>
> **Where it stops:** The broadening comes from Fourier mathematics, not optical focus. A window cannot reveal unrecorded samples or guarantee separation of nearby tones.

## Name the finite window you used

SciPy distinguishes a **periodic Hann window**, requested with `sym=False`, from a symmetric Hann, requested with `sym=True`. The periodic version is intended for spectral analysis; the symmetric version is commonly used for FIR design. A periodic window's final stored value need not be zero.

Their finite arrays have different sums. The average weight, called **coherent gain**, describes how the window scales a coherent tone under the usual separated-tone assumptions. For a periodic Hann with more than two samples, that average is one half. A symmetric Hann's average differs, so calculate the actual weight sum instead of assuming both conventions are interchangeable.

## Calibrate the tone you actually measured

For an isolated, bin-centred real tone at an interior frequency, replace the unwindowed sample-count denominator with the sum of the weights. This is exact when the mirrored negative-frequency tone contributes zero at the measured positive bin, and approximate when that contribution is negligible. Check the condition near DC or Nyquist and when changing windows.

```formula reference
A_k = (2|X_w[k]|) / S
S = Σ w[n]
where
A_k: estimated peak amplitude of the isolated bin-centred real tone, in the input signal's units
X_w[k]: unnormalised DFT coefficient of the windowed samples at interior positive-frequency bin k
|X_w[k]|: magnitude of the complex coefficient
k: bin where the mirrored negative-frequency tone contributes zero or negligibly
S: sum of all unitless window weights
Σ: add the weights for all acquired samples
w[n]: unitless window weight at sample index n
n: integer sample index across the acquired record
In words: for an isolated bin-centred tone whose positive and negative responses do not interfere, divide twice the windowed bin magnitude by the actual sum of window weights to estimate its peak amplitude.
```

This corrects window attenuation; it does not fix every peak error. A tone between bins can still have an underestimated largest bin, called **scalloping loss**. Nearby signals can also affect the peak. Noise PSD needs a different calibration based on squared weights and sample rate; use a documented estimator rather than reusing the coherent-tone correction.

## Key takeaways

- Leakage comes from finite observation and does not require noise.
- Hann suppresses side lobes while broadening the central response.
- State the window convention and distinguish coherent-tone correction from off-bin estimation and PSD scaling.

## Further reading

- [SciPy: Hann conventions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hann.html)
- [Steven W. Smith: applications of the DFT](https://www.dspguide.com/CH9.PDF)
- [SciPy: window sums and spectral scaling](https://docs.scipy.org/doc/scipy/tutorial/signal.html#spectral-analysis)
