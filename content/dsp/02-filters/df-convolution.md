---
id: df-convolution
title: Convolution as overlapping contributions
level: basic
minutes: 4
summary: Predict convolution by following overlapping responses, including zero extension and the output tail.
---

**Linear convolution** combines an input with an impulse response to predict the output of a zero-state LTI system. Each input sample launches a scaled copy of the response. When copies overlap, add their contributions. Unlike correlation, convolution models a system's response; it is not a template-similarity score.

## First add the copies

Suppose each input reading contributes its full value immediately and half its value one sample later. A single reading of 2 therefore produces 2 now and 1 next time. If another reading arrives before that response ends, the new response overlaps the old one. The output at that moment includes both contributions; the newer reading does not erase the earlier reading's influence.

There are two useful views of the same operation. Follow one input forward to see every output it affects, or stand at one output position and collect the input contributions that reach it. Keeping the timing aligned is what makes these views agree.

The last output remains after the final nonzero input. That **filter tail** is part of full convolution. This is linear convolution with zero extension: values outside either stored sequence are treated as zero. There is no wrapping from one end of an array to the other.

> [!analogy] Real-world analogy: overlapping payment plans
> Each purchase creates a payment today and a smaller payment next month. Several purchases can contribute to the same month's bill.
>
> **How it maps:** A purchase maps to an input sample; its fixed payment pattern maps to the impulse response. Adding the bills due in one month maps to adding overlapping contributions at one output sample.
>
> **Where it stops:** Real payment plans can include fees or changing terms. Convolution here assumes the same fixed linear response to every input, and sample values may also be negative.

## Keep the tail and the timing

If an input record contains four readings and each reading launches a three-position response, the last reading still has two positions of influence left after the record ends. Full convolution keeps those positions. Some may happen to contain zero; the full output length describes positions, not a count of nonzero values.

The optional reference below writes the output-side view. It also gives the full array length for two nonempty finite sequences.

```formula reference
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
In words: each output adds the response weights applied to the input readings that reach that moment; full convolution keeps the tail after the last input.
```

## Choose which outputs to retain

NumPy's `convolve` with `mode="full"` computes this discrete linear convolution for one-dimensional arrays. Other modes select fewer output positions; they do not create a physically different filter. Always choose which part of the full result your application needs. In particular, “same” length is an array-selection policy, not a guarantee of causal alignment.

## Key takeaways
- Convolution adds shifted, scaled impulse responses.
- Finite linear convolution uses zeros beyond the records and preserves a tail.
- State the output mode and alignment whenever comparing implementations.

## Further reading
- [Smith: convolution, Chapter 6](https://www.dspguide.com/CH6.PDF)
- [NumPy: convolve and its boundary modes](https://numpy.org/doc/stable/reference/generated/numpy.convolve.html)
