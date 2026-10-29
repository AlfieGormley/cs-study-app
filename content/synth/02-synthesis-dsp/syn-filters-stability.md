---
id: syn-filters-stability
title: Feedback stability and coefficient limits
level: intermediate
minutes: 3
summary: Feedback stability and coefficient limits.
sourceLesson: syn-filters
---

## Stability, intuitively

Feedback can run away. If the fraction fed back is too large, every sample adds more than the last and the output grows without limit.

For the one-pole, the previous output is multiplied by 1 − a every sample. Strict BIBO stability for the genuine non-cancelled one-pole response requires that multiplier’s magnitude below one. At the limiting coefficient settings, distinguish a non-decaying initial condition from forced growth; the zero-input behaviour alone is not the full BIBO definition:

```formula essential
|1 − a| < 1
0 < a < 2
where
|x|: absolute value: x without its sign
a: the one-pole coefficient; the filter is stable only for values strictly between 0 and 2
<: less than
In words: For the non-cancelled one-pole recurrence, the feedback multiplier must have magnitude below one so disturbances decay. A positive coefficient below two meets that condition; the positive exponential mapping keeps it below one.
```

For positive finite cutoff and sample rate, the exponential mapping gives a stable fixed filter in exact arithmetic. The shortcut replaces the exponential mapping with a coefficient proportional to cutoff, which can exceed two: at 48 kHz this occurs above about 15.3 kHz. Instability can therefore occur below Nyquist; checking the audio frequency limit alone is insufficient.

In general a digital IIR filter is stable when all its **poles** lie inside the unit circle. You don't need the theory yet; you need the habits:

- Clamp cutoff and resonance to the range the design supports.
- Compute coefficients with the design's own formulas, not approximations.
- Watch for NaN or infinity in the output during development, and reset the filter state if it appears.

## Key takeaways

- For this one-pole, stability requires the feedback multiplier magnitude below one.
- The shortcut coefficient can violate that condition below Nyquist.
- Clamp parameters to the actual supported range and detect non-finite output.

## Further reading

- [One-pole filter — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
- [Filter stability — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Filter_Stability.html)
