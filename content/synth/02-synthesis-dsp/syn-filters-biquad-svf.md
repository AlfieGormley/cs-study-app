---
id: syn-filters-biquad-svf
title: Choosing a biquad or state-variable filter
level: intermediate
minutes: 4
summary: Choosing a biquad or state-variable filter.
sourceLesson: syn-filters
---

## Resonant filter designs (conceptual)

You aren't expected to implement these yet. Know what they are, so you can pick one from a library and drive it well.

### Biquad (RBJ cookbook)

A general second-order IIR section, five coefficients:

```formula
y[n] = b_0 x[n] + b_1 x[n−1]
     + b_2 x[n−2]
     − a_1 y[n−1] − a_2 y[n−2]
where
y[n]: the output at sample n; y[n−1] and y[n−2] are the two previous outputs
x[n]: the input at sample n; x[n−1] and x[n−2] are the two previous inputs
n: the sample index
b_0, b_1, b_2: the feedforward coefficients, which act on inputs
a_1, a_2: the feedback coefficients, which act on past outputs (the cookbook divides every coefficient by a sixth one, a_0, so it does not appear)
In words: each output mixes the current and two previous inputs, minus a mix of the two previous outputs; the five numbers set the filter's type, cutoff and Q.
```

Robert Bristow-Johnson's **Audio EQ Cookbook** (now a W3C note) gives formulas for low-pass, high-pass, band-pass, notch, peaking and shelving filters from a centre or cutoff frequency (the cookbook’s frequency parameter), `Q` (or the width of the band) and gain. It's the standard choice for EQs. The cookbook's second-order low/high-pass responses approach 12 dB/oct in their analogue-style stopband region; two cascaded stages give 24 dB/oct. Notch, peaking and shelving biquads do not share that blanket slope rule.

Caveat: the common direct-form structures are known to behave poorly when coefficients change rapidly (fast cutoff sweeps): Wishnick (DAFx 2014) documents clicks when Direct Form II coefficients change, and a time-varying filter with feedback (IIR) can go unstable even when every individual coefficient set is stable. That's why synth filters often use other structures.

### State-variable filter (SVF)

A two-integrator loop that produces low-pass, band-pass and high-pass outputs at once, with cutoff and resonance controls that are nearly independent. The classic digital version (Chamberlin's) is very cheap but misbehaves at high cutoffs: its tuning drifts and, especially at low resonance, it goes unstable once the cutoff rises past roughly a seventh to a sixth of the sample rate (about 6.5 to 8.3 kHz at 48 kHz for Q between 0.5 and 0.707), so it is often run oversampled. Modern versions based on trapezoidal integration, such as Andrew Simper's (Cytomic), stay well-behaved when modulated quickly: Simper's paper states the filter remains stable and smooth even with audio-rate modulation, and Wishnick gives a proof of the SVF's stable time-varying behaviour. Those results apply to the stated integrator/state structure and supported positive, finite parameter ranges. They do not certify arbitrary SVF code, endpoint values, or finite-precision overflow.

## Key takeaways

- An RBJ biquad defines a second-order response through normalised coefficients.
- Fast coefficient changes require a structure and parameter range with appropriate time-varying stability evidence.

## Further reading

- [Audio EQ Cookbook — Robert Bristow-Johnson / W3C](https://www.w3.org/TR/audio-eq-cookbook/)
- [Trapezoidal state-variable filter — Andrew Simper](https://cytomic.com/files/dsp/SvfLinearTrapOptimised2.pdf)
- [Time-varying filters — Aaron Wishnick](https://www.dafx14.fau.de/papers/dafx14_aaron_wishnick_time_varying_filters_for_.pdf)
