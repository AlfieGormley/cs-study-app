---
id: syn-filters-iir-fir
title: Impulse responses, IIR and FIR
level: intermediate
minutes: 3
summary: Impulse responses, IIR and FIR.
sourceLesson: syn-filters
---

## IIR and FIR

The one-pole filter feeds its own previous output back. Its **impulse response** is the output after a single input sample of one followed by zeros.

After the impulse, each output feeds a fraction of itself into the next output. With the stable coefficient used here, that tail shrinks but never reaches exact zero in ideal arithmetic.

That makes it an **infinite impulse response (IIR)** filter.

A conventional feedforward **finite impulse response (FIR)** filter uses only current and past *inputs*.

It multiplies a finite set of recent inputs by chosen weights, called **taps**, and adds them. Once an isolated impulse has passed every tap, no copy remains to contribute to later output.

For example, averaging the current and two previous input samples with equal one-third weights gives a three-tap moving average. It has a low-pass main lobe but also zeros and sidelobes; it is not a monotonic textbook one-pole.

| | IIR | FIR |
|---|---|---|
| Feedback | yes | no |
| Cost for a steep slope | low | high (many taps) |
| BIBO stable with fixed finite coefficients | Depends on poles | Yes |
| Exact non-trivial linear phase | Generally incompatible with causal stable IIR | Possible with appropriate symmetry |

The table compares common direct implementations. FIR describes the finite response; equivalent feedback-based implementations of some FIR responses can also exist.

Many common synth resonant filters are IIR because feedback produces sharp responses with few operations. Fixed finite-coefficient FIR filters are BIBO stable: bounded input gives bounded output. An FIR can also form a resonant magnitude peak; it simply has no infinite ringing tail. Symmetric FIR designs can give exact linear phase and are useful in resampling. Finite-precision overflow, unbounded changing coefficients and nonlinear processing need separate analysis.

## Key takeaways

- A feedback one-pole has an infinite impulse response in exact arithmetic.
- A fixed finite FIR has bounded output for bounded input.
- Linear-phase FIR designs are possible; do not infer all IIR responses share one phase rule.

## Further reading

- [Filter stability — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Filter_Stability.html)
- [Linear-phase FIR filters — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Linear_Phase_Filters_Symmetric_Impulse.html)
