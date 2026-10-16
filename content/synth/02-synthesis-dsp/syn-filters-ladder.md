---
id: syn-filters-ladder
title: The ladder model and cutoff modulation
level: intermediate
minutes: 4
summary: The ladder model and cutoff modulation.
sourceLesson: syn-filters
---

### Ladder

Robert Moog's patented transistor ladder: four one-pole low-pass stages in series (24 dB/oct) with negative feedback from the output to the input. Stilson and Smith's analysis models the feedback gain `k` from 0 to 4: in its ideal linear model, the response becomes marginal at feedback 4, with imaginary-axis poles at the individual stage corner frequency. The ideal response diverges at that frequency as feedback approaches the threshold. Real sustained self-oscillation is amplitude-limited by circuit nonlinearities; the linear model does not predict its final amplitude. Two well-known traits follow from the model: resonance comes with a drop in low-frequency level (worked out below), and the feedback loop has no delay, so digital versions need care (a unit delay in the loop, or an implicit/zero-delay-feedback solution).

```diagram
x -->(+)--[LP]--[LP]--[LP]--[LP]--+--> y
      ^                           |
      |                           |
      +----------(-k)-------------+
```

The model's response shows where the bass loss comes from:

```formula
H(s) = 1 / (k + (1 + s / ω_c)^4)
H(0) = 1 / (k + 1)
G_0 = 20 log_10(1 / (3 + 1)) ≈ −12 dB
where
H(s): the filter's transfer function: its gain and phase shift at complex frequency s
s: the Laplace variable (complex frequency); for a steady sine of angular frequency ω, s = j × ω, where j is the imaginary unit (the square root of −1), so s = 0 means DC (0 Hz)
ω_c: omega c, the corner frequency of each individual one-pole stage in radians per second; it is not generally the composite ladder’s half-power cutoff
k: the resonance feedback gain, from 0 (none) to 4 (self-oscillation)
H(0): the gain at DC, i.e. the very lowest frequencies
G_0: that DC gain in decibels, for k = 3
log_10: the base-10 logarithm
dB: decibels
≈: approximately equal to
In words: each stage passes DC unchanged (the fourth-power term becomes 1), so the gain there is 1/(k + 1); turning resonance up to k = 3 cuts the bass by about 12 dB.
```

> [!tip] Drive cutoff in octaves
> Pitch, envelope and LFO modulation of cutoff should add in octaves (log frequency), then convert once, as below. Clamp the result to a safe range (e.g. 20 Hz up to somewhat below Nyquist) before computing coefficients.

```formula
f_c = f_base 2^{o}
f_c = 500 Hz × 2^{1.5} ≈ 1414 Hz
where
f_c: the cutoff actually used, in hertz (Hz)
f_base: the cutoff set by the knob, in Hz
o: the total modulation in octaves (envelope, LFO, key tracking added together), positive or negative
2^{o}: 2 raised to the power o: +1 octave doubles the cutoff, −1 halves it
Hz: hertz
≈: approximately equal to
In words: add up all the modulation in octaves, then convert once by doubling the cutoff for every octave.
```

## Key takeaways

- The ideal four-stage ladder feedback model explains resonance and bass loss.
- A marginal self-oscillation threshold is not a bounded practical oscillator model.
- Combine cutoff contributions in octaves and clamp before using the chosen design.

## Further reading

- [Analysis of the Moog ladder — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf)
- [Trapezoidal state-variable filter — Andrew Simper](https://cytomic.com/files/dsp/SvfLinearTrapOptimised2.pdf)
