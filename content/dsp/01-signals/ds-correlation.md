---
id: ds-correlation
title: Find a template with correlation
level: intermediate
minutes: 3
summary: Interpret a sliding template match without mistaking a large score for proof.
---

**Cross-correlation** scores how well a known **template** matches data at different shifts. A distinctive sensor pulse may be recognisable even when its starting position is unknown. At each shift, multiply aligned values and add them. A strong positive score can indicate a positive match, but raw score also depends on amplitude, offset and overlap length.

## Define the lag before interpreting it

This lesson uses real, unitless finite sequences and the sign convention of SciPy’s `correlate(data, template)`. Treat values outside either stored record as zero. **Lag** is the integer shift of the template relative to the data origin; a positive lag places the template’s start later in the data.

For data `[0, 0, 1, -1, 0]` and template `[1, -1]`, the complete pattern starts at data index 2. The best positive match is therefore at lag +2 samples. At that position, positive aligns with positive and negative with negative; both products contribute positively. Shifting the template one place either way aligns opposite signs and gives a negative score.

For complex inputs, SciPy conjugates the shifted template before multiplying. Conjugation reverses the imaginary sign; it leaves a real template unchanged, so the real-valued example needs no extra operation. Reversing the input order reverses the lag interpretation. Never guess the sign from the word correlation alone.

> [!analogy] Real-world analogy: Sliding a transparent pattern
> Slide a transparent strip with a distinctive pattern across a longer strip and look for alignment.
>
> **How it maps:** The short strip is the template; its position is lag. Correlation combines agreement over corresponding positions into one score.
>
> **Where it stops:** Numerical products allow negative values, amplitude weighting and cancellation. A visual match alone does not define those arithmetic rules.

Do not assume that the position in a returned score array is the lag. Full correlation includes partial overlaps before the template reaches the data’s start, so its lag labels can begin below zero. Obtain the labels explicitly; SciPy provides `correlation_lags` for this purpose.

## Similarity is not a guarantee

Doubling the data amplitude doubles every raw score, including negative scores. An increased peak therefore does not necessarily mean a closer match in shape. A large DC offset can dominate scores when the template has a nonzero mean. Subtracting appropriate means can help compare fluctuating shape, but also changes what is being detected.

Normalising by the overlapping magnitudes can reduce amplitude dependence. The method must specify which overlap is measured and what happens when it contains only zeros, where division by its magnitude would fail. No such normalisation is applied here.

At extreme full-mode lags only a few samples overlap. Their scores are not automatically comparable to a full-template overlap. `valid` mode excludes positions requiring zero padding, provided the data is at least as long as the template. Repeated patterns or noise can produce misleading peaks; report ambiguity rather than assuming a single physical delay.

Correlation compares a sliding template in its original order. **Convolution**, introduced next module, uses a reversal in the sliding sum and describes how a system combines shifted responses. They share arithmetic ingredients but have different index definitions and purposes.

## Key takeaways
- State input order, lag convention and record boundaries.
- Obtain lag labels explicitly rather than using an output array index.
- Raw correlation depends on shape, amplitude, offset and overlap; a peak is evidence to interpret.

## Further reading
- [SciPy: correlation definition and boundary modes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html)
- [SciPy: explicit correlation lag labels](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlation_lags.html)
