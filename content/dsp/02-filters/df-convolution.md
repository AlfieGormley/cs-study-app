---
id: df-convolution
title: Convolution as overlapping contributions
level: basic
minutes: 5
summary: Compute finite linear convolution, including zero extension and the output tail.
---

**Linear convolution** combines an input with an impulse response to predict the output of a zero-state LTI system. Each input sample launches a scaled copy of the response. When copies overlap, add their contributions. Unlike correlation, convolution models a system's response; it is not a template-similarity score.

## First add the copies

Take input `[2, 1, 3]` and impulse response `[1, 0.5]`, both starting at sample zero. The first input launches `[2, 1]`. The next launches `[1, 0.5]` one sample later. The third launches `[3, 1.5]` two samples later. Adding aligned entries produces `[2, 2, 3.5, 1.5]`.

The last output remains after the final nonzero input. That **filter tail** is part of full convolution. This is linear convolution with zero extension: values outside either stored sequence are treated as zero. There is no wrapping from one end of an array to the other.

## Then write the weighted sum

The capital Greek letter sigma means “add the following terms”. The lower limit starts the counter at zero; the upper limit includes the last coefficient. The counter changes inside the sum while the output index stays fixed.

```formula
y[n] = Σ_{k=0}^{M−1} h[k]x[n − k]
L = N + M − 1
where
y: the output sequence, with dimensionless sample values here
x: the input sequence of N samples; zero outside indices zero through N minus one
h: the impulse response of M dimensionless coefficients; zero outside indices zero through M minus one
n: the output sample index, from zero through L minus one
k: the integer coefficient index, counting from zero through M minus one
M: the positive integer number of impulse-response coefficients
N: the positive integer number of input samples
L: the number of samples in the full output array, including its tail
Σ_{k=0}^{M−1}: finite summation; evaluate the following product for each integer k from zero through M minus one and add the results
In words: multiply each response weight by the appropriately delayed input, add the contributions, and keep enough output samples for every overlap.
```

Some final output values may happen to be zero; the length formula describes the full array, not the number of nonzero results. For three input samples and two weights it gives four output positions. At output sample two, the present input contributes 3 and the previous input contributes 0.5.

## Implement the input-side view

This complete example starts an all-zero output and adds one shifted response for each input sample. Python `enumerate` supplies each index alongside its value.

```python
x = [2.0, 1.0, 3.0]
h = [1.0, 0.5]
y = [0.0] * (len(x) + len(h) - 1)
for i, sample in enumerate(x):
    for k, weight in enumerate(h):
        y[i + k] += sample * weight
print(y)
# [2.0, 2.0, 3.5, 1.5]
```

NumPy's `convolve` with `mode="full"` computes this discrete linear convolution for one-dimensional arrays. Other modes select fewer output positions; they do not create a physically different filter. Always choose which part of the full result your application needs. In particular, “same” length is an array-selection policy, not a guarantee of causal alignment.

## Key takeaways
- Convolution adds shifted, scaled impulse responses.
- Finite linear convolution uses zeros beyond the records and preserves a tail.
- State the output mode and alignment whenever comparing implementations.

## Further reading
- [Smith: convolution, Chapter 6](https://www.dspguide.com/CH6.PDF)
- [NumPy: convolve and its boundary modes](https://numpy.org/doc/stable/reference/generated/numpy.convolve.html)
