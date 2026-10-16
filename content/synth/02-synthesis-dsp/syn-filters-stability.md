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

```formula
|1 − a| < 1
0 < a < 2
a_sc = (2πf_c) / f_s
f_max = f_s / π
f_max = 48000 Hz / 3.14159 ≈ 15279 Hz
where
|x|: absolute value: x without its sign
a: the one-pole coefficient; the filter is stable only for values strictly between 0 and 2
<: less than
a_sc: the coefficient given by a common shortcut formula
π: pi, about 3.14159
f_c: the cutoff, in hertz (Hz)
f_s: the sample rate, in Hz
f_max: the cutoff at which the shortcut's coefficient reaches 2; above it the filter is unstable
Hz: hertz
≈: approximately equal to
In words: the filter is stable while the feedback multiplier 1 − a stays between −1 and 1; the exp formula always keeps a between 0 and 1, but the shortcut passes 2 once the cutoff exceeds the sample rate divided by π.
```

So the exp formula is always stable, but with the shortcut, sweeping the cutoff above about 15.3 kHz at 48 kHz makes the filter blow up.

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
