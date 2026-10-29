---
id: syn-filters-resonance-q
title: Resonance, Q and headroom
level: intermediate
minutes: 3
summary: Resonance, Q and headroom.
sourceLesson: syn-filters
---

## Resonance and Q

A resonant filter boosts frequencies **near the cutoff** before rolling off. On a synth this is the **resonance** (or emphasis) control. Turn it up and the filter "sings" at the cutoff frequency; sweep it and you hear the classic wah.

**Q** (quality factor) controls damping and response shape in the two-pole low-pass family discussed here. A Q of about 0.7071 (one divided by the square root of 2) is the **Butterworth** value: maximally flat, no peak, −3 dB at cutoff. For this low-pass family, raising Q above the maximally flat value creates an increasingly strong resonance. The maximum generally lies near, rather than exactly at, the design frequency. For the RBJ cookbook low-pass, the gain at the cutoff frequency equals Q.

For example, a quality factor of 4 gives four times the input amplitude at the design frequency, about a 12 dB boost. The maximum response may lie elsewhere, so measure peaks across the band when setting output gain.

A numerical check at a 48 kHz sample rate with a 1 kHz cutoff confirms it:

| Q | Gain at the design frequency |
|---|---|
| 0.7071 | −3.0 dB |
| 2 | +6.0 dB |
| 4 | +12.0 dB |
| 10 | +20.0 dB |

At high enough resonance, some filters **self-oscillate**: the peak becomes so strong that the filter rings at its cutoff with no input, effectively becoming a sine oscillator. Analogue players use this deliberately.

## Key takeaways

- Q controls the RBJ low-pass response; gain at its design frequency equals Q.
- Resonance consumes headroom; self-oscillation depends on the design.

## Further reading

- [Audio EQ Cookbook — Robert Bristow-Johnson / W3C](https://www.w3.org/TR/audio-eq-cookbook/)
- [Analysis of the Moog ladder — Stilson and Smith](https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf)
