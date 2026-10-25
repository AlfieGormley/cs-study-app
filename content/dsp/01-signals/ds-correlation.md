---
id: ds-correlation
title: Find a template with correlation
level: intermediate
minutes: 5
summary: Trace a finite correlation and interpret its lag sign carefully.
---

**Cross-correlation** scores how well a known **template** matches data at different shifts. A distinctive sensor pulse may be recognisable even when its starting position is unknown. At each shift, multiply aligned values and add them. A strong positive score can indicate a positive match, but raw score also depends on amplitude, offset and overlap length.

## Define the lag before interpreting it

This lesson uses real, unitless finite sequences and the same sign convention as SciPy’s `signal.correlate(data, template, mode="full")`. Treat values outside either stored record as zero. **Lag** is the integer shift of the template relative to the data origin; a positive lag places the template’s start later in the data.

```formula
r[k] = Σ x[n] t[n−k]
0 ≤ n ≤ N − 1
−(M − 1) ≤ k ≤ N − 1
where
r: real unitless cross-correlation scores
k: integer lag, in samples; positive places the template later in x
Σ: add one product for each integer n from 0 through N − 1 inclusive
n: integer data sample index
N: positive number of data samples
x: unitless data sequence
t: unitless template sequence, zero outside its stored indices
M: positive number of template samples
In words: Shift the template, multiply corresponding samples and add; full mode includes every lag with at least one overlapping pair.
```

For data `[0, 0, 1, -1, 0]` and template `[1, -1]`, the best positive score is 2 at lag +2: the template starts at data index 2. At lag +1 the score is −1, and at lag +3 it is −1. The complete lag range is −1 through +4, giving `[0, 0, -1, 2, -1, 0]`.

For complex inputs, SciPy conjugates the shifted template before multiplying. Conjugation reverses the imaginary sign; it leaves a real template unchanged, so the real formula above needs no extra operation. Reversing the input order reverses the lag interpretation. Never guess the sign from the word correlation alone.

> [!analogy] Real-world analogy: Sliding a transparent pattern
> Slide a transparent strip with a distinctive pattern across a longer strip and look for alignment.
>
> **How it maps:** The short strip is the template; its position is lag. Correlation combines agreement over corresponding positions into one score.
>
> **Where it stops:** Numerical products allow negative values, amplitude weighting and cancellation. A visual match alone does not define those arithmetic rules.

## Execute the convention

This complete NumPy/SciPy example uses one-dimensional arrays. `correlation_lags` labels each output position, so an array index is not mistaken for a lag. `argmax` returns the position of the largest value, taking the first if there is a tie. The direct method uses sums rather than Fourier acceleration.

```python
import numpy as np
from scipy import signal
x = np.array([0, 0, 1, -1, 0])
t = np.array([1, -1])
r = signal.correlate(x, t, mode='full',
                     method='direct')
lags = signal.correlation_lags(
    len(x), len(t), mode='full')
i = int(np.argmax(r))
print(r.tolist())
print(int(lags[i]), int(r[i]))
# [0, 0, -1, 2, -1, 0]
# 2 2: lag in samples, then score
```

## Similarity is not a guarantee

Doubling the data amplitude doubles raw scores. A large DC offset can dominate scores when the template has a nonzero mean. Subtracting appropriate means can help compare fluctuating shape, but also changes what is being detected. Normalising by the overlapping magnitudes can reduce amplitude dependence; it needs an explicit boundary and zero-energy policy. No such normalisation is applied here.

At extreme full-mode lags only a few samples overlap. Their scores are not automatically comparable to a full-template overlap. `valid` mode excludes positions requiring zero padding, provided the data is at least as long as the template. Repeated patterns or noise can produce misleading peaks; report ambiguity rather than assuming a single physical delay.

Correlation compares a sliding template in its original order. **Convolution**, introduced next module, uses a reversal in the sliding sum and describes how a system combines shifted responses. They share arithmetic ingredients but have different index definitions and purposes.

## Key takeaways
- State input order, lag convention and record boundaries.
- Obtain lag labels explicitly rather than using an output array index.
- Raw correlation depends on shape, amplitude, offset and overlap; a peak is evidence to interpret.

## Further reading
- [SciPy: correlation definition and boundary modes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html)
- [SciPy: explicit correlation lag labels](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlation_lags.html)
