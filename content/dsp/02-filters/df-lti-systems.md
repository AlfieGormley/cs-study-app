---
id: df-lti-systems
title: Two tests for a predictable system
level: basic
minutes: 4
summary: Test linearity and time invariance, and understand why initial state belongs in the assumptions.
---

A **discrete-time system** takes an input sequence and produces an output sequence. Multiplying every sensor reading by two is a system. So is smoothing several readings or clipping values above a limit. Before choosing a filter, ask which mathematical shortcuts its behaviour permits.

## Linearity means preserving combinations

A **linear system** preserves scaling and addition together. Processing a mixture must give the same result as processing its components separately and then mixing their outputs with the same weights. This property is **superposition**. It must hold for every allowed pair of inputs and every allowed constant weight; one successful example cannot prove it.

Think of two sensors feeding a mixer. A linear filter lets you filter each sensor separately and then mix, or mix first and filter once, with the same result. This is useful because a complicated signal can be understood through simpler components. It is a property of the processing rule, not a claim that the output graph looks like a straight line.

The optional notation records that same test for entire sequences.

```formula reference
T(ax + bv) = aT(x) + bT(v)
where
T: the system operation, mapping an entire input sequence to an output sequence
x: the first input sequence, with dimensionless sample values in this example
v: the second input sequence, in the same dimensionless units as x
a: a constant dimensionless weight for the first sequence
b: a constant dimensionless weight for the second sequence
In words: combining weighted inputs before processing must match combining the separately processed outputs with those same weights.
```

Doubling every reading passes this test. Squaring fails because doubling an input makes its squared result four times as large, rather than twice as large. Adding a constant offset also fails: zero input produces a nonzero output. Zero input producing zero output is necessary for linearity, though it is not a sufficient test by itself. Clipping is another common failure: a quiet mixture may pass unchanged while a louder mixture hits the limit.

## Time invariance means the same rule later

A **time-invariant system** gives an equally shifted output when its entire input is shifted. A fixed one-sample delay passes: sending a pulse three samples later moves the delayed pulse three samples later too. Multiplying each sample by its absolute sample index fails: an identical pulse gets a different gain when it arrives later.

Linearity and time invariance are separate tests. A fixed squaring operation is time invariant but nonlinear. Multiplication by the sample index is linear but time varying. A system that passes both is **linear time-invariant**, or **LTI**. Fixed weighted sums of present and past inputs are important examples.

> [!analogy] Real-world analogy: an unchanged recipe
> Doubling two ingredients and combining batches works predictably when the recipe scales consistently. Preparing the same batch tomorrow should also give the same result.
>
> **How it maps:** Scaling and combining batches suggest linearity; applying the same recipe on a later day suggests time invariance.
>
> **Where it stops:** Real cooking is rarely linear. Temperature, vessel size and chemical changes can break both predictions.

## Include the initial state

Filters may remember earlier samples. **Zero state** means their stored history is initially zero. An input/output linearity test must include that assumption: a filter already holding a nonzero output can respond even to zero new input.

For time-shift comparisons, shift the complete input history and use the corresponding zero-state setup. Restarting a device midway through one run changes the experiment. Likewise, finite-array truncation can hide a delayed output; compare the whole relevant output, including its tail.

## Key takeaways
- Linearity preserves weighted combinations; time invariance preserves shifts.
- One counterexample disproves either property.
- State and record boundaries must be part of an LTI claim.

## Further reading
- [Smith: linear systems, Chapter 5](https://www.dspguide.com/CH5.PDF)
- [Julius O. Smith: LTI digital filters](https://www.dsprelated.com/freebooks/filters/Linear_Time_Invariant_Digital_Filters.html)
