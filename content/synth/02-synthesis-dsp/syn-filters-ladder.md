---
id: syn-filters-ladder
title: The ladder model and cutoff modulation
level: intermediate
minutes: 3
summary: The ladder model and cutoff modulation.
sourceLesson: syn-filters
---

### Ladder

Robert Moog's patented transistor ladder: four one-pole low-pass stages in series (24 dB/oct) with negative feedback from the output to the input. Stilson and Smith's analysis models the feedback gain `k` from 0 to 4: in its ideal linear model, the response becomes marginal at feedback 4, with imaginary-axis poles at the individual stage corner frequency. The ideal response diverges at that frequency as feedback approaches the threshold. Real sustained self-oscillation is amplitude-limited by circuit nonlinearities; the linear model does not predict its final amplitude. Two well-known traits follow from the model: resonance comes with a drop in low-frequency level (explained below), and the feedback loop has no delay, so digital versions need care (a unit delay in the loop, or an implicit/zero-delay-feedback solution).

```diagram
x -->(+)--[LP]--[LP]--[LP]--[LP]--+--> y
      ^                           |
      |                           |
      +----------(-k)-------------+
```

The model's response shows where the bass loss comes from.

At very low frequencies, each ideal stage passes the signal without attenuation, but the overall negative feedback still reduces gain. Increasing feedback therefore changes both the resonant peak and the bass level. In this uncompensated model, a feedback gain of 3 leaves one quarter of the original DC amplitude, about 12 dB down.

> [!tip] Drive cutoff in octaves
> Pitch, envelope and LFO modulation of cutoff should add in octaves (log frequency), then convert once, as below. Clamp the result to the range supported by the exact filter implementation before computing coefficients. Being below Nyquist alone does not establish a safe cutoff or resonance.

Add cutoff modulation in octaves before converting to frequency: one octave doubles the base cutoff, two quadruple it, and a negative octave halves it. Combining contributions first keeps every route in the same musical unit.

## Key takeaways

- The ideal four-stage ladder feedback model explains resonance and bass loss.
- A marginal self-oscillation threshold is not a bounded practical oscillator model.
- Combine cutoff contributions in octaves and clamp before using the chosen design.

## Further reading

- [Analysis of the Moog ladder — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf)
- [Trapezoidal state-variable filter — Andrew Simper](https://cytomic.com/files/dsp/SvfLinearTrapOptimised2.pdf)
