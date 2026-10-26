---
id: ds-quantisation-clipping
title: Quantisation and clipping
level: basic
minutes: 3
summary: Separate rounding to levels from losing values beyond the range.
---

Sampling chooses times. **Quantisation** chooses representable amplitude levels. These are different restrictions: increasing the sample rate does not make the amplitude steps finer. A digital value may represent volts, temperature or a unitless normalised amplitude; know the conversion before interpreting its size.

A **bit** has two possible states. Three bits can label eight different codes. The voltage range, coding and rounding rules still need specification: a bit count alone does not define a complete converter.

## Small rounding errors and lost peaks

Imagine a toy quantiser with levels spaced by 0.25, from −1 to 0.75. An input of 0.30 rounds to 0.25. Small input changes can leave the output unchanged until it crosses the boundary to the next level. Finer steps can preserve smaller amplitude changes within the available range.

An exact halfway input needs a stated tie rule. If this toy chooses the more positive neighbour, −0.375 becomes −0.25 rather than −0.5. Another rule could choose differently. Specify the spacing, endpoints and rounding rule before predicting exact output values; the bit count alone is insufficient.

For nearest-level rounding without range limiting, error magnitude is at most half a step. That bound does not protect over-range inputs. **Clipping**, also called saturation, caps excessive values at an endpoint. In this toy, inputs of 1.0 and 1.5 both become 0.75. Their different peak heights are lost.

> [!analogy] Real-world analogy: Marks and ends on a ruler
> A short ruler has marked divisions and also a final endpoint.
>
> **How it maps:** Rounding a length to the nearest mark resembles quantisation. Reporting every length beyond the ruler as its maximum resembles clipping.
>
> **Where it stops:** Real measurements can have other errors; the ruler comparison does not make quantisation error random or independent.

## Choose the remedy for the problem

If small changes disappear between amplitude levels, consider finer quantisation over the required range. Increasing sample rate alone changes the time spacing, not those levels. Increasing bit depth can provide more levels, but the chosen input range still matters.

If peaks reach the endpoint, reduce input gain before the range-limited stage or choose an appropriate input range. Making an already clipped record quieter only shrinks its flat peaks; it cannot infer their original heights.

Quantisation error also depends on the signal and rounding scheme. A repeated input can produce a repeated error, so do not automatically treat that error as independent white noise. These lessons distinguish the mechanisms rather than assuming a noise model that fits every input.

## Key takeaways
- Sampling selects times; quantisation selects amplitude levels.
- Specify the grid, endpoints and tie rule before predicting a quantiser.
- Clipping can cause errors far larger than half a step and loses information.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH3.PDF)
