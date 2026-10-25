---
id: ds-mean-rms
title: Mean, peak and RMS
level: basic
minutes: 5
summary: Measure a finite record’s offset and overall level with the correct units.
---

One number cannot describe every property of a signal. A sensor record can have a steady offset, a fluctuating component and occasional large excursions. **Record mean**, **peak magnitude** and **root mean square (RMS)** answer different questions. This lesson uses a non-empty finite record of real values; these are exact record descriptions, not estimates of an unknown infinite process.

## Mean and DC offset

The mean adds all samples and divides by the count. **DC** originally means direct current; in DSP a DC component is a constant offset. The record mean is the constant you subtract to centre that record at zero.

The summation symbol means repeat the indicated term for each integer index, starting at the lower limit and including the upper limit, then add the results.

```formula
μ = (Σ x[n]) / N
0 ≤ n ≤ N − 1
z[n] = x[n] − μ
where
μ: record mean, in the signal’s units
Σ: finite sum; add one term for each integer n from 0 through N − 1 inclusive
n: unitless integer sample index
N: positive number of samples in the record
x: original real-valued signal, in its physical units or unitless
z: centred signal, in the same units as x
In words: Average the samples to find the offset; subtract that average from every sample to centre this record.
```

For `[1, 3]` volts the mean is 2 volts and the centred samples are `[-1, 1]` volts. The offset might be unwanted sensor bias, or it might be the actual quantity being measured. Do not remove it automatically. A short slice of a changing signal can have a nonzero mean without the underlying source having a permanent offset.

## Peak and RMS

Peak magnitude is the largest absolute sample value. RMS squares the samples, averages the squares and takes a square root. Squaring prevents positive and negative values cancelling. The final root restores the original units.

```formula
P = max(|x[0]|, …, |x[N−1]|)
R = √((Σ x[n]^2) / N)
0 ≤ n ≤ N − 1
where
P: peak sample magnitude, in the signal’s units
max: choose the greatest of the listed magnitudes
| |: absolute value, the non-negative magnitude of a real number
x: real-valued signal, in physical units or unitless
N: positive number of samples
n: integer index from 0 through N − 1
…: include every intervening sample
R: RMS of the complete record, in the signal’s units
√: non-negative square root
Σ: add one squared sample for each integer n from 0 through N − 1 inclusive
In words: Peak checks the largest excursion; RMS measures the square-root of the average squared level, including any offset.
```

For `[1, 3]` volts, the peak is 3 volts and the RMS is about 2.236 volts. After centring, the RMS becomes 1 volt. Mean zero does not mean no signal: `[-1, 1]` has zero mean but a nonzero RMS.

This complete example computes the three descriptions directly. `abs` takes a magnitude; `sum` adds values; `len` counts them. The empty-record guard avoids dividing by zero or asking for a nonexistent maximum.

```python
import math
x = [1.0, 3.0]  # volts
if not x:
    raise ValueError('record is empty')
mean = sum(x) / len(x)
peak = max(abs(v) for v in x)
rms = math.sqrt(sum(v*v for v in x)
                / len(x))
print(mean, peak, round(rms, 6))
# 2.0 3.0 2.236068
```

RMS has a connection to physical power only with a specified model, such as voltage across a fixed resistor. Squared temperature values are not automatically watts. Peak sample magnitude also need not equal the maximum of a continuous waveform between sampling instants.

## Key takeaways
- Mean describes offset; subtracting it changes the measured signal.
- Peak checks extremes; RMS includes both offset and fluctuations.
- Mean, peak and RMS retain the original signal units.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH2.PDF)
