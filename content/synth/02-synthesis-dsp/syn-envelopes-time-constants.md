---
id: syn-envelopes-time-constants
title: Exponential segments and time constants
level: intermediate
minutes: 4
summary: Exponential segments and time constants.
sourceLesson: syn-envelopes
---

Assume a positive time constant, positive sample rate and a fixed finite target. The envelope values here are dimensionless gain/control values. A zero-time segment needs an explicit immediate-transition branch; the coefficient formula divides by the time constant.

### Exponential (one-pole) segments

Analogue envelope generators charge and discharge a capacitor through a resistor, which gives exponential curves. Digitally, that is a **one-pole filter** moving towards a target: each sample, the level moves a fixed fraction of the remaining distance.

```formula
y[n] = y[n−1] + c(g − y[n−1])
c = 1 − exp(−1 / (τf_s))
c = 1 − exp(−1 / (0.01 s × 48000 Hz))
c = 1 − exp(−1/480) ≈ 0.00208
where
y[n]: the envelope level at sample n; y[n−1] is the level one sample earlier
c: the coefficient: the fraction of the remaining distance covered each sample, between 0 and 1
g: the target level the segment is heading for (the peak, the sustain level or 0)
exp: the exponential function, e raised to a power, where e ≈ 2.71828
τ: tau, the time constant, in seconds (s); here 10 ms = 0.01 s
f_s: the sample rate, in hertz (Hz), here 48,000
s: seconds
Hz: hertz, per second
≈: approximately equal to
In words: each sample the level closes a small fixed fraction of the gap to the target, so it moves fast when far away and slows as it gets close; a longer time constant means a smaller fraction and a slower curve.
```

In the code this is `y += c * (target - y)`. The coefficient is chosen so that the remaining distance shrinks by a factor of e every τ seconds. `tau` (τ) is the **time constant**: after τ seconds the level has covered 63.2% of the distance to the target. In general:

```formula
r(t) = 1 − exp(−t / τ)
t = τ ln(1 / (1 − r))
r = 0.99: t = τ ln(100) ≈ 4.6τ
where
r(t): the fraction of the distance to the target covered after time t, from 0 to 1
t: the time since the segment started, in seconds (s)
τ: tau, the time constant, in seconds
exp: the exponential function, e raised to a power (e ≈ 2.71828)
ln: the natural logarithm, the inverse of exp: ln(exp(x)) = x
r: the fraction you want to reach, e.g. 0.99 for 99%
≈: approximately equal to
s: seconds
In words: after one time constant the level is 63.2% of the way there (1 − 1/e); reaching 99% takes about 4.6 time constants and 99.9% about 6.9.
```

Measured at 48 kHz with τ = 10 ms:

| Fraction reached | Time |
|---|---|
| 63.2% | 10.0 ms |
| 99% | 46.1 ms (4.6 τ) |
| 99.9% | 69.1 ms (6.9 τ) |

An exponential approach never quite arrives, which creates two practical issues:

1. **Attack:** if the target is 1.0 the attack never ends. Common fix: aim *past* the peak (say 1.2) and switch to decay when the level crosses 1.0.
2. **Release:** the level gets ever smaller without reaching 0. Stop at a threshold (e.g. 1e-5, which is −100 dB) and mark the voice idle so the voice allocator can reuse it. Very tiny floating-point values (subnormals) can also be slow on some processors.

## Key takeaways

- One time constant closes about 63% of a fixed-target gap.
- State whether a time control means a time constant or a time to a specified threshold.
- Exponential attack and release need explicit end conditions.

## Further reading

- [ADSR implementation — Nigel Redmon](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)
- [Time constant of one pole — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/Time_Constant_One_Pole.html)
- [Subnormal floating-point numbers — Intel](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2024-2/subnormal-numbers.html)
