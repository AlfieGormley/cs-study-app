---
id: dp-fast-convolution
title: FFT convolution without wrapping the tail
level: intermediate
minutes: 4
summary: Turn circular FFT multiplication into full linear convolution and preserve block tails with overlap-add.
---

FFT multiplication can calculate convolution efficiently, but the transform's boundary model matters. A fixed-length DFT treats its input as repeating. Multiplying the transforms and taking an inverse FFT therefore gives **circular convolution**: contributions beyond the chosen length wrap back to the beginning.

Ordinary finite filtering with zero extension needs linear convolution instead. The solution is to reserve space for the complete output, including its filter tail, before transforming.

## Make room before multiplying

For a four-sample input and a three-coefficient FIR, the full output occupies six positions. Pad both transforms to at least that full length. Using only the length of the longer input generally leaves too little room.

```formula essential
Q = N + K − 1
M ≥ Q
where
Q: full linear-convolution output length, in samples
N: input record length, in samples
K: FIR coefficient count
M: shared FFT length used for both inputs
≥: greater than or equal to
In words: the full output needs the input length plus the filter length minus one positions; both FFTs must be at least that long to avoid wrapping the tail into the beginning.
```

A longer FFT can be chosen for efficiency. After the inverse transform, keep the full linear output length; extra padded positions are not additional physical output. Small floating-point errors can remain.

> [!analogy] Real-world analogy: a circular calendar
> Write a long task schedule on a repeating weekly calendar. Anything that spills past Sunday appears back under Monday unless you reserve enough distinct dates.
>
> **How it maps:** Circular convolution wraps the tail into earlier positions. Sufficient padding reserves space for every linear-convolution contribution before the repetition begins.
>
> **Where it stops:** The FFT combines numeric contributions by addition, and its wrap is an exact mathematical boundary rule. Padding removes that wrap for finite linear convolution; it does not remove a filter's actual tail.

## Recognise wraparound in a result

For input `[1, 2, 3, 4]` and FIR `[1, 1, 1]`, full linear convolution is `[1, 3, 6, 9, 7, 4]`. A four-point FFT product instead returns `[8, 7, 6, 9]`. The final tail has been added into the beginning, not discarded or substituted for the first samples.

This gives a useful diagnosis: if the end of a filtered record contaminates its beginning, inspect transform length and padding before changing the filter coefficients. Compare with direct full convolution on a small input to check the boundary behaviour.

## Add block responses at their original positions

For a long signal, **overlap-add** processes input blocks separately with the same FIR. Each block needs sufficient FFT padding for its own full convolution. Place that result at the output position corresponding to the block's original start.

Adjacent results overlap because each block keeps producing a filter tail after its last input sample. Add contributions at shared positions. Concatenating full block outputs shifts later responses; overwriting the overlap loses contributions.

When full finite output is requested, retain the last tail after the final input block. A streaming implementation also needs buffering, latency and flushing policies. Overlap-add does not guarantee zero latency. SciPy provides `fftconvolve` for FFT convolution and `oaconvolve` for overlap-add; actual speed depends on lengths and hardware.

## Key takeaways

- FFT multiplication naturally uses circular boundaries.
- Pad both transforms for the full linear output to prevent wraparound.
- Overlap-add combines shared positions and keeps the final tail when full output is required.

## Further reading

- [Steven W. Smith: FFT convolution and overlap-add](https://www.dspguide.com/CH18.PDF)
- [SciPy: full FFT convolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.fftconvolve.html)
- [SciPy: overlap-add convolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.oaconvolve.html)
