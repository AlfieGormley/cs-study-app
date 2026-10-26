---
id: prob-normal-z-scores
title: Read normal probabilities using z-scores
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: A normal model is specified by its mean and positive standard deviation.
---

A **normal distribution** is a continuous symmetric bell curve. Its mean locates the centre and its positive standard deviation sets the spread. A larger spread makes the same absolute distance from the centre less unusual.

## Standardise distance

A **z-score** describes how many standard deviations a value lies above or below the mean. Subtract the mean and divide by the standard deviation. Positive values are above the mean; negative ones are below. This comparison needs a finite positive standard deviation, but computing a z-score does not itself make data normal.

```formula reference
z = (x − μ) / σ
where
z: the z-score of x, with no units
x: one particular value
μ: mu, the mean
σ: sigma, the positive standard deviation, in the same units as the observations
In words: Subtract the mean and divide by the positive standard deviation to express distance from the centre in units of spread.
```

Under a normal model, roughly 68% of observations lie within one standard deviation of the mean, 95% within two and 99.7% within three. These are two-sided bands. The upper edge of the three-standard-deviation band is about the 99.865th percentile, because only half the remaining probability lies above it.

## Use the model, not just the scale

For a normal response-size model with mean 500 kilobytes and standard deviation 50 kilobytes, 600 kilobytes is two standard deviations above the mean. If spread doubles while the mean stays fixed, that same response is less unusual.

A normal law allows all real values. For a nonnegative quantity it can only be an approximation, and its negative tail may be unacceptable. A z-score alone does not give a tail probability for an arbitrary distribution; use the distributional model or measured observations.

## Key takeaways
- Mean and standard deviation control location and spread in a normal model.
- Z-scores compare distance on a common scale.
- Normal percentage bands are two-sided and are not universal rules.

## Further reading
- [Normal distribution — NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm)
