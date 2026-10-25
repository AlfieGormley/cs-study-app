---
id: ds-quantisation-clipping
title: Quantisation and clipping
level: basic
minutes: 5
summary: Separate rounding to levels from losing values beyond the range.
---

Sampling chooses times. **Quantisation** chooses representable amplitude levels. These are different restrictions: increasing the sample rate does not make the amplitude steps finer. A digital value may represent volts, temperature or a unitless normalised amplitude; know the conversion before interpreting its size.

A **bit** has two possible states. Three bits can label eight different codes. The voltage range, coding and rounding rules still need specification: a bit count alone does not define a complete converter.

## A fully specified toy quantiser

Our toy converts unitless input values to the eight levels from −1 to 0.75, spaced by 0.25. It rounds to the nearest level, taking an exact halfway tie towards the more positive value. It then restricts the result to the available range. This is a teaching convention, not a claim about every ADC or Python’s built-in `round`.

```formula
Δ = 0.25
q(x) = Δ floor(x / Δ + 0.5)
y = min(0.75, max(−1, q(x)))
e = y − x
where
Δ: spacing between neighbouring unitless output levels
x: unitless input value
q: rounding function to a multiple of Δ before range limiting
floor: greatest integer no larger than its argument
y: unitless output after range limiting
min: function returning the smaller argument
max: function returning the larger argument
e: unitless output error, defined as output minus input
In words: Round to the grid using the stated tie rule, then limit the result to the available endpoints.
```

For an input of 0.30 the output is 0.25, with an error of −0.05. For 0.375, exactly halfway between two levels, the output is 0.50. For −0.375 the tie goes to −0.25, because that is the more positive level.

Without range limiting, nearest-level rounding has error magnitude at most half a step. That small-error bound does not protect inputs beyond the representable range. **Clipping** or saturation limits excessive values to an endpoint; an input of 1.50 becomes 0.75, losing 0.75. Many different high inputs then produce the same output.

> [!analogy] Real-world analogy: Marks and ends on a ruler
> A short ruler has marked divisions and also a final endpoint.
>
> **How it maps:** Rounding a length to the nearest mark resembles quantisation. Reporting every length beyond the ruler as its maximum resembles clipping.
>
> **Where it stops:** Real measurements can have other errors; the ruler comparison does not make quantisation error random or independent.

## Run the exact convention

This complete Python example uses `math.floor` rather than `round`, whose halfway rule differs. The nested `min` and `max` implement the range limits. All numbers here are unitless.

```python
import math
def quantise(x):
    step = 0.25
    q = step * math.floor(x / step + 0.5)
    return min(0.75, max(-1.0, q))
xs = [0.30, 0.375, -0.375, 1.50]
print([quantise(v) for v in xs])
# [0.25, 0.5, -0.25, 0.75]
```

Quantisation error depends on the input and rounding scheme. A repeated input can produce a repeated error; do not assume all quantisation errors are white noise. Reducing an already clipped record’s gain makes the flat peaks smaller but cannot infer their original heights.

## Key takeaways
- Sampling selects times; quantisation selects amplitude levels.
- Specify the grid, endpoints and tie rule before predicting a quantiser.
- Clipping can cause errors far larger than half a step and loses information.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH3.PDF)
