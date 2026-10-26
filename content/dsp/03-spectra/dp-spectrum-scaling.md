---
id: dp-spectrum-scaling
title: Calibrating a spectrum
level: basic
minutes: 4
summary: Recover real-tone amplitudes without doubling DC or Nyquist, and distinguish amplitude from power density.
---

A raw FFT magnitude is a sum over samples. A longer record can therefore produce a larger raw peak even when the physical tone has stayed equally strong. Before interpreting a spectrum, ask what its vertical axis measures and how the software normalises it.

An **amplitude spectrum** reports tone size in the input's units, such as volts. A **power spectral density**, or **PSD**, reports mean-square content per unit bandwidth. They answer different questions and need different scaling.

## Turn a raw peak into a tone amplitude

Start with a controlled case: NumPy's default unnormalised forward FFT, a real record, no tapering window and an isolated tone exactly centred on an interior bin. A **bin-centred** tone completes a whole number of cycles in the record.

Divide the coefficient magnitude by the acquired sample count. Then double it for an ordinary positive-frequency tone: a real sinusoid has matching positive and negative frequency contributions, and a one-sided amplitude plot combines that pair.

```formula reference
A_k = (2|X[k]|) / N
where
A_k: peak amplitude of the isolated bin-centred real sinusoid, in the input signal's units
X[k]: unnormalised complex DFT coefficient at interior positive-frequency bin k
|X[k]|: non-negative magnitude of that complex coefficient
N: acquired sample count, with no padding or tapering window
k: positive-frequency bin with a distinct negative-frequency partner, excluding DC and Nyquist
In words: for an isolated bin-centred real tone without a taper, divide the raw bin magnitude by the acquired sample count and double it to combine the positive and negative frequency contributions.
```

If the same steady tone is recorded for twice as long, the raw magnitude doubles under these assumptions; the calibrated amplitude stays the same. That is a useful check for a length-dependent calibration bug.

## Treat the endpoints separately

DC has no separate negative-frequency partner. Neither does the Nyquist bin in an even-length real record. Divide their magnitudes by the sample count without doubling. For odd lengths, every returned real-FFT bin after DC has a partner because there is no exact Nyquist bin.

DC magnitude gives the absolute mean. To preserve the sign of an offset, use the signed real DC coefficient instead. The Nyquist component describes an alternating sampled sequence; it cannot establish an arbitrary continuous sinusoid's amplitude because sampling exactly at Nyquist has phase ambiguity.

Changing the FFT normalisation or applying a window changes the calibration. An off-bin tone spreads across bins, so its largest bin alone generally underestimates its peak even after this simple correction.

## Choose the quantity you need

Peak amplitude is useful for asking how large an isolated vibration or voltage tone is. Mean-square power describes a signal's average squared size. An ordinary sinusoid, averaged over whole cycles, contributes half its squared peak amplitude to mean square. Electrical watts require an additional circuit relationship; square volts alone are not watts.

PSD distributes mean-square power over frequency. For voltage input, its units are square volts per hertz. Multiplying each density by its bin width and summing estimates mean square under the estimator's window and detrending conventions. More densely spaced bins must not create extra total power.

SciPy's `periodogram` offers `scaling="density"` for PSD and `scaling="spectrum"` for a squared-magnitude spectrum. Its default detrending removes the mean; use `detrend=False` if DC must remain. Tapered PSD uses window-energy normalisation, so simply squaring doubled tone amplitudes is not a general PSD recipe. A tapered estimate also need not match the unweighted finite record's mean square exactly.

## Key takeaways

- Record the FFT normalisation, window, sample count and units before interpreting a peak.
- Combine paired bins for one-sided tone amplitude; leave DC and an even-length Nyquist bin undoubled.
- Choose amplitude for tone size and PSD for mean-square content per bandwidth.

## Further reading

- [NumPy: FFT normalisation conventions](https://numpy.org/doc/stable/reference/routines.fft.html)
- [SciPy: periodogram scaling and units](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html)
