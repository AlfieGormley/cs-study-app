---
id: syn-filters-one-pole-state
title: The one-pole recurrence and per-voice state
level: intermediate
minutes: 3
summary: The one-pole recurrence and per-voice state.
sourceLesson: syn-filters
---

This audio filter uses finite input samples and a positive cutoff/sample rate. Its state is independent for each separately filtered voice. Alternatively, sum voices first and intentionally filter the mix once; that shares a filter envelope rather than interleaving unrelated streams through one state.

## The one-pole low-pass

The simplest useful filter. Its **difference equation** says how each output sample is computed:

```formula
y[n] = y[n−1] + a(x[n] − y[n−1])
y[n] = a x[n] + (1 − a)y[n−1]
where
x[n]: the input sample at step n
y[n]: the output sample at step n; y[n−1] is the previous output
n: the sample index (0, 1, 2...); [n−1] means one sample earlier
a: the filter coefficient, between 0 and 1; small a means heavy smoothing (a low cutoff)
In words: each output moves a fraction a of the way from the previous output towards the new input; the second line is the same rule rearranged as a weighted average of the new input and the old output.
```

It's the same formula as the envelope and smoother in the envelope units, now running on audio. For example, with a = 0.1227, starting from 0, a step input (x jumps from 0 to 1 and stays there) gives outputs of 0.1227, 0.230, 0.325...: an exponential rise towards 1.

The coefficient comes from the cutoff (one standard choice, also used by EarLevel Engineering):

```formula
a = 1 − exp(−(2πf_c / f_s))
a = 1 − exp(−2π × 1000 / 48000)
a = 1 − exp(−0.1309) ≈ 0.1227
where
a: the one-pole coefficient
exp: the exponential function, e (about 2.71828) raised to a power
π: pi, about 3.14159
f_c: the cutoff frequency, in hertz (Hz), here 1 kHz
f_s: the sample rate, in Hz, here 48,000
≈: approximately equal to
In words: the coefficient depends on the cutoff as a fraction of the sample rate; a higher cutoff gives a bigger a (less smoothing), and a always stays between 0 and 1.
```

The **state** is the single number `y[n-1]`. It must persist across samples and blocks, exactly like oscillator phase, and each voice needs its own.

## Key takeaways

- The recurrence mixes the new input with the previous output.
- Preserve state across blocks and use separate state for independent voices.
- A filter on the summed signal is a deliberate shared-filter architecture.

## Further reading

- [One-pole filter — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
- [One-pole filter — Nigel Redmon](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
