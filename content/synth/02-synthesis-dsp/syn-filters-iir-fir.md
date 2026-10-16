---
id: syn-filters-iir-fir
title: Impulse responses, IIR and FIR
level: intermediate
minutes: 3
summary: Impulse responses, IIR and FIR.
sourceLesson: syn-filters
---

## IIR and FIR

The one-pole filter feeds its own output back (the previous output). Its **impulse response** (the output when you feed in a single 1 followed by zeros) is:

```formula
h[n] = a(1 − a)^{n}
h[0] = 0.1227, h[1] ≈ 0.1076, h[2] ≈ 0.0944
where
h[n]: the impulse response: the output n samples after a single 1 was fed in
a: the coefficient, here 0.1227
n: the number of samples since the impulse
≈: approximately equal to
In words: each sample the output shrinks by the factor 1 − a, so it decays for ever without ever quite reaching zero.
```

That makes it an **infinite impulse response (IIR)** filter.

A **finite impulse response (FIR)** filter uses only current and past *inputs*:

```formula
y[n] = b_0 x[n] + b_1 x[n−1]
     + … + b_N x[n−N]
where
y[n]: the output at sample n
x[n]: the input at sample n; x[n−1] is one sample earlier and x[n−N] is N samples earlier
b_0, b_1, b_N: the filter's coefficients (its **taps**), fixed numbers chosen by the design
N: the filter's order: how many past inputs it uses
…: and so on: one term for every delay in between
In words: each output is a weighted sum of the current input and the last N inputs, with no feedback, so an impulse passes through in N + 1 samples and is gone.
```

For example, averaging the current and two previous input samples with equal one-third weights gives a three-tap moving average. It has a low-pass main lobe but also zeros and sidelobes; it is not a monotonic textbook one-pole.

| | IIR | FIR |
|---|---|---|
| Feedback | yes | no |
| Cost for a steep slope | low | high (many taps) |
| BIBO stable with fixed finite coefficients | Depends on poles | Yes |
| Exact non-trivial linear phase | Generally incompatible with causal stable IIR | Possible with appropriate symmetry |

Many common synth resonant filters are IIR because feedback produces sharp responses with few operations. Fixed finite-coefficient FIR filters are BIBO stable: bounded input gives bounded output. An FIR can also form a resonant magnitude peak; it simply has no infinite ringing tail. Symmetric FIR designs can give exact linear phase and are useful in resampling. Finite-precision overflow, unbounded changing coefficients and nonlinear processing need separate analysis.

## Key takeaways

- A recursive one-pole has an infinite impulse response in exact arithmetic.
- A fixed finite FIR has bounded output for bounded input.
- Linear-phase FIR designs are possible; do not infer all IIR responses share one phase rule.

## Further reading

- [Filter stability — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Filter_Stability.html)
- [Linear-phase FIR filters — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Linear_Phase_Filters_Symmetric_Impulse.html)
