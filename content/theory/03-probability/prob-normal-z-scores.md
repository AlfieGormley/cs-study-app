---
id: prob-normal-z-scores
title: Read normal probabilities using z-scores
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: A normal model is specified by its mean and positive standard deviation.
---

## Normal: the bell curve

The **normal distribution** (Gaussian) is continuous (it can take any real value), symmetric, and described by just two numbers, its mean and its standard deviation. The **68–95–99.7 rule** says how much of it lies within one, two and three standard deviations of the mean:

```formula
X ~ N(μ, σ^2)
P(|X − μ| ≤ σ) ≈ 0.683
P(|X − μ| ≤ 2 × σ) ≈ 0.954
P(|X − μ| ≤ 3 × σ) ≈ 0.997
where
X: a normally distributed random variable
~: "is distributed as"
N(μ, σ^2): the normal distribution with mean μ and variance σ^2
μ: mu, the mean, the centre of the bell
σ: sigma, the standard deviation, the width of the bell; greater than 0
σ^2: the variance, σ squared
|X − μ|: the distance of X from the mean, ignoring direction (absolute value)
P: probability; probabilities are dimensionless and apply to measurable events
≤: less than or equal to
≈: approximately equal to
Conditioning: every event to the right of a given bar in this card has positive probability
In words: about 68% of values lie within one standard deviation of the mean, 95% within two and 99.7% within three.
```

The bell shape, with the mean in the middle and one and two standard deviations either side:

```
          ____
        /|    |\
      /  |    |  \
   __/   |    |   \__
 ---+----+----+----+---
  μ−2σ  μ−σ  μ+σ  μ+2σ

```

A **z-score** says how many standard deviations a value is from the mean:

```formula
z = (x − μ) / σ
P(Z > 1.96) ≈ 0.025
where
z: the z-score of x, with no units
x: one particular value
μ: mu, the mean
σ: sigma, the positive standard deviation, in the same units as the observations
Z: a **standard normal** variable, a normal with mean 0 and standard deviation 1
P: probability; probabilities are dimensionless and apply to measurable events
1.96: the z-score that cuts off the top 2.5%, so 95% lies between −1.96 and +1.96
≈: approximately equal to
In words: a value 1.96 standard deviations above the mean is beaten only 2.5% of the time.
```

This is where the "1.96" in 95% confidence intervals comes from (the later confidence-interval unit). For example, if response sizes are normal with mean 500 KB and standard deviation 50 KB:

```formula
z = (600 KB − 500 KB) / (50 KB) = 2
where
z: the z-score of a 600 KB response, in standard deviations
500: the mean size, in kilobytes (KB)
50: the standard deviation, in KB
KB: kilobyte, 1,000 bytes
In words: a 600 KB response is two standard deviations above the mean, so only about 2.3% of responses are larger.
```

## Key takeaways
- A normal model is specified by its mean and positive standard deviation.
- A z-score measures distance from the mean in standard deviations.

## Further reading
- [Normal distribution — NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm)
