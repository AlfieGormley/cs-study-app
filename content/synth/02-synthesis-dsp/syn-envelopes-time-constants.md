---
id: syn-envelopes-time-constants
title: Exponential segments and time constants
level: intermediate
minutes: 3
summary: Exponential segments and time constants.
sourceLesson: syn-envelopes
---

Assume a positive time constant, positive sample rate and a fixed finite target. The envelope values here are dimensionless gain/control values. A zero-time segment needs an explicit immediate-transition branch; the coefficient formula divides by the time constant.

### Exponential (one-pole) segments

Analogue envelope generators charge and discharge a capacitor through a resistor, which gives exponential curves. Digitally, that is a **one-pole filter** moving towards a target: each sample, the level moves a fixed fraction of the remaining distance.

```formula reference
y[n] = y[n−1] + c(g − y[n−1])
c = 1 − exp(−1 / (τf_s))
where
y[n]: the envelope level at sample n; y[n−1] is the level one sample earlier
n: the sample index
c: the coefficient: the fraction of the remaining distance covered each sample, between 0 and 1
g: the target level the segment is heading for (the peak, the sustain level or 0)
exp: the exponential function, e raised to a power, where e ≈ 2.71828
τ: tau, the time constant, in seconds (s); here 10 ms = 0.01 s
f_s: the sample rate, in hertz (Hz), here 48,000
s: seconds
Hz: hertz, per second
≈: approximately equal to
In words: Each sample closes a fixed fraction of the remaining gap to the target. The motion slows as it approaches; a longer time constant gives a slower curve.
```

In the code this is `y += c * (target - y)`. The **time constant** is a fixed duration describing how quickly the remaining gap shrinks.

After one time constant, about 63.2% of the initial gap has closed. Reaching 99% takes about 4.6 time constants and reaching 99.9% takes about 6.9. A time constant describes the curve, not when the segment finishes.

For a release towards zero, the same time constant takes the same time to reach a given fraction of its starting level, regardless of the starting amplitude. A fixed absolute stopping threshold differs: a louder start needs longer to fall to that threshold.

For a 10 ms time constant at 48 kHz:

| Fraction reached | Time |
|---|---|
| 63.2% | 10.0 ms |
| 99% | 46.1 ms |
| 99.9% | 69.1 ms |

An exponential approach never quite arrives, which creates two practical issues:

1. **Attack:** if the target is 1.0 the attack never ends. Common fix: aim *past* the peak (say 1.2) and switch to decay when the level crosses 1.0.
2. **Release:** the level gets ever smaller without reaching 0. Stop at a threshold (e.g. 1e-5, which is −100 dB) and mark the voice idle so the voice allocator can reuse it. Very tiny floating-point values (subnormals) can also be slow on some processors.

> [!analogy] Real-world analogy: Closing half the remaining gap
> Imagine taking a fixed fraction of the remaining distance towards a door on every step. The steps become smaller as you approach.
>
> **How it maps:** The one-pole moves a fixed fraction of its remaining error, so it slows near the target and needs an explicit end condition.
>
> **Where it stops:** The fraction need not be one half, real motion is continuous, and finite arithmetic can eventually round to a target.

## Key takeaways

- One time constant closes about 63% of a fixed-target gap.
- State whether a time control means a time constant or a time to a specified threshold.
- Exponential attack and release need explicit end conditions.

## Further reading

- [ADSR implementation — Nigel Redmon](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)
- [Time constant of one pole — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Time_Constant_One_Pole.html)
- [Subnormal floating-point numbers — Intel](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2024-2/subnormal-numbers.html)
