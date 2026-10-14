---
id: snd-digital-gain-staging
title: Stage gain and protect the output
level: intermediate
minutes: 3
summary: Place headroom and protection in a float synth and measure worst-case patches.
sourceLesson: snd-levels
---

## Gain staging inside a digital synth

**Gain staging** means setting the level at each stage so that no stage clips and none is needlessly quiet. In a floating-point synth, intermediate stages almost never clip, so the concerns are different from analogue gear:

```flow
Oscillators, each about -6 to -12 dBFS
Voice mixer: scale for the number of sources
Filter: resonance can boost near cutoff
Amp envelope and velocity
Voice sum: scale for polyphony
Effects: check for level build-up
Master gain, then soft clip or limiter
Convert to the codec format (hard limit)
```

Practical rules:

1. **Know where the hard limit is.** In a float pipeline it's the final conversion. Everything before can exceed 1.0 temporarily.
2. **Budget headroom where levels can grow:** summing voices, resonant filters (which can boost signals near the cutoff well above the input level) and feedback effects.
3. **Protect the output.** A soft clipper or limiter just before conversion turns rare overshoots into mild saturation instead of harsh clipping.
4. **Measure.** Log peak and RMS in an offline render of your worst case: all voices, full resonance, maximum velocity.
5. **Change gain smoothly.** Jumping a gain value between samples causes clicks; stepping it in coarse increments when a knob turns causes "zipper noise". Smoothing is covered in the synthesis module.

## Key takeaways

- Budget headroom for mixing, resonance and feedback effects.
- Intermediate float signals can exceed nominal full scale; protect the final fixed-format conversion.
- Measure worst-case peak and RMS, and smooth control changes to avoid clicks and zipper noise.

## Further reading

- [dBFS — Wikipedia](https://en.wikipedia.org/wiki/DBFS)
- [Gain stage — Wikipedia](https://en.wikipedia.org/wiki/Gain_stage)
