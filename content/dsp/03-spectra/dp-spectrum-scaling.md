---
id: dp-spectrum-scaling
title: Calibrating a spectrum
level: basic
minutes: 5
summary: Recover real-tone amplitudes without doubling DC or Nyquist, and distinguish amplitude from power density.
---

Raw FFT magnitudes change when the record length changes. A useful **amplitude spectrum** needs an explicit normalisation and units. This lesson uses NumPy's default unnormalised forward FFT, an even-length real record, no tapering window, and tones exactly centred on bins. These conditions matter.

## Recover a tone's peak amplitude

A **bin-centred** tone completes a whole number of cycles in the record. An ordinary real sinusoid splits its contribution between a positive-frequency bin and its negative-frequency partner. A one-sided amplitude plot combines that pair by doubling the positive-bin magnitude after dividing by the record length.

```formula
A_k = (2|X[k]|) / N
A_k = (2 × 24 V) / 16 = 3 V
where
A_k: peak amplitude of an isolated bin-centred real sinusoid at interior bin k, in the input's units; here volts (V)
X[k]: unnormalised complex DFT coefficient at bin k, here with magnitude 24 V
|X[k]|: complex magnitude of X[k], a non-negative real number
N: even record length, here 16 samples, with no zero padding or taper
k: interior positive-frequency bin, from 1 through (N / 2) − 1
V: volt, the unit of the input measurement
In words: a raw interior-bin magnitude of 24 from sixteen samples represents a three-volt peak sinusoid.
```

DC has no separate partner. Neither does the Nyquist bin in an even-length record. Divide their magnitudes by the record length without doubling. DC magnitude gives the absolute mean; retain the signed real DC coefficient if the sign of the offset matters. The Nyquist result describes an alternating sampled sequence, not an arbitrary continuous sinusoid's amplitude: sampling at exactly Nyquist has phase ambiguity.

```formula
A_0 = |X[0]| / N
A_{N/2} = |X[N/2]| / N
where
A_0: magnitude of the DC offset, in the input signal's units
A_{N/2}: magnitude of the alternating Nyquist component, in the input signal's units
X: unnormalised DFT coefficient array of the real input
| |: magnitude of the coefficient between the bars
N: even number of real input samples, without zero padding or taper
In words: the two unpaired endpoints are divided by the record length and are not doubled.
```

## Complete Python example

`abs` takes complex magnitudes. The slice `1:-1` selects all coefficients except DC and Nyquist. This slice is correct here because the input length is even; for odd lengths, double every returned coefficient after DC.

```python
import numpy as np

n = np.arange(16)
x = 2 + 3 * np.cos(2 * np.pi * n / 16)
x = x + 0.5 * (-1.0) ** n
a = abs(np.fft.rfft(x)) / len(x)
a[1:-1] *= 2
print(np.round(a[[0, 1, 8]], 6))
# Offset, cosine peak, alternating peak.
```

The output is `[2.  3.  0.5]`. Changing the transform's `norm` option changes its scaling; do not reuse this recipe unchanged with another convention.

## Amplitude, mean-square power and PSD

Amplitude retains the sample's units, such as volts. An isolated non-DC, non-Nyquist sinusoid has mean-square value equal to half its squared peak amplitude, when averaged over whole cycles. Thus a three-volt peak cosine contributes 4.5 square volts to mean square. This is signal power in a mean-square sense; electrical watts additionally require an appropriate circuit relationship, such as a known resistance.

A **power spectral density**, or **PSD**, distributes mean-square power per unit bandwidth. For voltage input its units are square volts per hertz. Summing PSD values multiplied by bin spacing estimates mean-square power under the chosen window and detrending convention. For a tapered periodogram this is a window-weighted estimate; it need not equal the unweighted finite record's mean square exactly. A denser grid alone must not create extra total power.

SciPy's `periodogram(..., scaling="density")` returns a PSD; `scaling="spectrum"` returns a squared-magnitude spectrum. Its default detrending removes the mean. Set `detrend=False` when DC must remain. Window energy is used for density scaling; coherent tone-amplitude scaling uses a different normalisation. Squaring this lesson's doubled amplitude values is not a general PSD recipe.

## Key takeaways

- State the FFT normalisation, window, record length and units before interpreting a number.
- Double only paired bins in a real one-sided amplitude spectrum.
- Peak amplitude, mean-square power and power per hertz answer different questions.

## Further reading

- [NumPy: FFT normalisation conventions](https://numpy.org/doc/stable/reference/routines.fft.html)
- [SciPy: periodogram scaling and units](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.periodogram.html)
