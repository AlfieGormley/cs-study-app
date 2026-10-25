---
id: dp-fast-convolution
title: FFT convolution without wrapping the tail
level: intermediate
minutes: 5
summary: Turn circular FFT multiplication into full linear convolution and preserve block tails with overlap-add.
---

Convolution can be calculated by taking both inputs' FFTs, multiplying corresponding coefficients and taking an inverse FFT. The catch is the boundary model: a fixed-length DFT treats its input as repeating. Multiplication therefore produces **circular convolution**, where output contributions beyond the chosen length wrap back to the beginning.

For ordinary finite filtering with zero extension, we want linear convolution. Make enough room for its entire tail before transforming.

## Pad both inputs to a sufficient length

```formula
Q = N + K − 1
M ≥ Q
Q = 4 + 3 − 1 = 6
where
Q: full linear-convolution output length in samples
N: first input length, here 4 samples
K: second input or FIR coefficient length, here 3 samples
M: shared FFT length for both inputs, at least Q
≥: greater than or equal to
In words: four samples convolved with three coefficients require six output positions; pad both transforms to at least six points.
```

After the inverse transform, retain the full linear-convolution length. A larger FFT length may be chosen for efficiency, but the extra positions are not extra physical output. Small floating-point errors are expected. Choosing an FFT length equal only to the longer input is generally insufficient.

> [!analogy] Real-world analogy: a circular calendar
> Write a long task schedule on a repeating weekly calendar. Anything that spills past Sunday appears back under Monday unless you reserve enough distinct dates.
>
> **How it maps:** Circular convolution wraps the tail into earlier positions. Sufficient padding reserves space for every linear-convolution contribution before the repetition begins.
>
> **Where it stops:** The FFT combines numeric contributions by addition, and its wrap is an exact mathematical boundary rule. Padding removes that wrap for finite linear convolution; it does not remove a filter's actual tail.

## Complete Python example

`ifft` is NumPy's inverse transform; with the default convention it includes the reciprocal-length scaling. These inputs are dimensionless, so their convolution is dimensionless. `.real` discards only tiny numerical imaginary errors expected for real inputs here.

```python
import numpy as np

x = np.array([1., 2., 3., 4.])
h = np.array([1., 1., 1.])
def fft_product(size):
    X = np.fft.fft(x, n=size)
    H = np.fft.fft(h, n=size)
    return np.fft.ifft(X * H).real

print(np.round(fft_product(4), 6))
print(np.round(fft_product(6), 6))
print(np.convolve(x, h, mode="full"))
```

The short transform gives `[8. 7. 6. 9.]`: the final linear values 7 and 4 have wrapped into the first two positions. The padded transform and direct convolution both give `[1. 3. 6. 9. 7. 4.]`.

## Overlap-add for long signals

**Overlap-add** splits the input into blocks, computes each block's full linear convolution with the same FIR, and adds it into the output at that block's original starting index. Adjacent results overlap because each block has a filter tail. They must be added, not concatenated or overwritten.

For a four-sample input split into `[1, 2]` and `[3, 4]`, the three-tap example produces `[1, 3, 3, 2]` and `[3, 7, 7, 4]`. Start the second result two positions after the first and add the overlap: the full result is again `[1, 3, 6, 9, 7, 4]`.

Each block's FFT length must accommodate that block plus the FIR tail. Retain the last tail after the final input block when the application requests full output. Streaming implementations need a policy for buffering, latency and flushing; overlap-add is not a promise of zero latency. SciPy's `fftconvolve(..., mode="full")` handles full finite convolution, while `oaconvolve` uses overlap-add. Actual speed depends on lengths and hardware.

## Key takeaways

- FFT multiplication naturally has circular boundaries.
- Pad to at least the full linear output length to prevent wraparound.
- Overlap-add adds neighbouring tails and flushes the final tail when full output is required.

## Further reading

- [Steven W. Smith: FFT convolution and overlap-add](https://www.dspguide.com/CH18.PDF)
- [SciPy: full FFT convolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.fftconvolve.html)
- [SciPy: overlap-add convolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.oaconvolve.html)
