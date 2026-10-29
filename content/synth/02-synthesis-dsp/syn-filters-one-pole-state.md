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

```formula essential
y[n] = y[n−1] + a(x[n] − y[n−1])
where
x[n]: the input sample at step n
y[n]: the output sample at step n; y[n−1] is the previous output
n: the sample index (0, 1, 2...); [n−1] means one sample earlier
a: the filter coefficient, between 0 and 1; small a means heavy smoothing (a low cutoff)
In words: Each new output moves a chosen fraction of the way from the previous output towards the current input. A small fraction smooths heavily; the stored previous output is the filter’s memory.
```

This is the same remaining-gap rule used by the envelope and smoother, now running on audio. When the input jumps to a new constant value, the output approaches it quickly at first and then more slowly; the step size shrinks as the gap closes.

The coefficient comes from the cutoff (one standard choice, also used by EarLevel Engineering):

```formula reference
a = 1 − exp(−(2πf_c / f_s))
where
a: the one-pole coefficient
exp: the exponential function, e (about 2.71828) raised to a power
π: pi, about 3.14159
f_c: the cutoff frequency, in hertz (Hz), here 1 kHz
f_s: the sample rate, in Hz, here 48,000
In words: This coefficient mapping gives less smoothing as the requested cutoff rises. For positive finite settings it keeps the coefficient between zero and one; the requested cutoff approximates the half-power point only well below Nyquist.
```

The **state** is the single number `y[n-1]`. It must persist across samples and blocks, exactly like oscillator phase, and each voice needs its own.

> [!analogy] Real-world analogy: A moving average with a memory
> A cautious tracker moves partway from its previous estimate towards each new observation.
>
> **How it maps:** The stored output is the estimate; the new audio sample is the observation; the coefficient sets how quickly the estimate responds.
>
> **Where it stops:** The filter acts at audio rates and changes phase as well as level. This comparison does not predict an exact cutoff.

## Key takeaways

- The recurrence mixes the new input with the previous output.
- Preserve state across blocks and use separate state for independent voices.
- A filter on the summed signal is a deliberate shared-filter architecture.

## Further reading

- [One-pole filter — Julius O. Smith](https://ccrma.stanford.edu/~jos/filters/One_Pole.html)
- [One-pole filter — Nigel Redmon](https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/)
