---
id: aud-acoustics-source-addition
title: Combine unrelated and coherent sources
level: basic
minutes: 4
summary: Uncorrelated sources add in mean-square pressure, giving about three decibels for two equal sources.
sourceLesson: aud-acoustics
---

## Adding sources

Independent sound sources (for example unrelated noise sources) can be treated as **incoherent sources** over the averaging interval: their waveforms are unrelated, so their mean-square pressures add, with the correlation cross-term averaging to zero. To add levels, turn each one back into a relative mean-square pressure, add those values, and turn the total back into decibels:

```formula
L_total = 10 log_10(Σ 10^{L_i / 10})
where
L_total: the combined level at the listening position, in dB SPL
L_i: the level of source number i on its own, at the same position, in dB SPL
i: a counter that runs over the sources: 1, 2, 3 and so on
10^{L_i / 10}: the relative power of source i (10 raised to the power of its level divided by 10)
Σ: sigma, "sum of": add up the term for every source
log_10: the base-10 logarithm
In words: convert each level to a power, add the powers, and convert back to decibels with 10 × log because these are powers, not pressures.
```

Worked example, two equal 90 dB SPL sources, then a 90 and an 80:

```formula
L_total = 10 log_10(10^9 + 10^9)
L_total = 10 log_10(2 × 10^9)
L_total = 10 × 9.301 ≈ 93.01 dB SPL
L_mix = 10 log_10(10^9 + 10^8)
L_mix = 10 log_10(1.1 × 10^9)
L_mix = 10 × 9.0414 ≈ 90.41 dB SPL
where
L_total: the combined level of two 90 dB SPL sources, in dB SPL
L_mix: the combined level of a 90 dB SPL and an 80 dB SPL source, in dB SPL
log_10: the base-10 logarithm
10^9: the relative power of a 90 dB source (10 to the power 90 / 10)
10^8: the relative power of an 80 dB source
dB: decibels
SPL: sound pressure level
≈: approximately equal to
In words: two equal unrelated sources give 3 dB more than one; adding a source 10 dB quieter raises the total by only about 0.4 dB.
```

This assumes the sources really are unrelated and you average over a long enough time. The same sum as a program:

```python
import math

def lsum(*levels):
    # Sum uncorrelated mean-square
    # pressures.
    return 10 * math.log10(
        sum(10 ** (l / 10) for l in levels))

print(round(lsum(90, 90), 2))
print(round(lsum(90, 80), 2))
print(round(lsum(90, 90, 90, 90), 2))
```

```output
93.01
90.41
96.02
```

- Two equal incoherent sources: **+3 dB**.
- A source 10 dB quieter adds only about 0.4 dB. The loud one dominates.
- Four equal sources: +6 dB.

**Coherent sources** are different. Two speakers playing the *same* signal at the same distance add in pressure, so they can give up to **+6 dB** where they arrive in phase, and deep cancellation where they arrive out of phase. Compare doubling the pressure with doubling the power:

```formula
ΔL_coh = 20 log_10(2) ≈ +6.02 dB
ΔL_inc = 10 log_10(2) ≈ +3.01 dB
where
ΔL_coh: the gain from adding a second, identical, in-phase copy (pressure doubles), in decibels (dB)
ΔL_inc: the gain from adding a second, equal but unrelated source (power doubles), in decibels (dB)
Δ: delta, "change in"
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibels
In words: two identical in-phase copies double the pressure (+6 dB); two equal unrelated sources double the power (+3 dB).
```
 For delayed broadband copies, the repeating frequency peaks and notches are **comb filtering**; a single tone instead shows spatial interference, and it is why the microphone units’ 3:1 rule and the crossover units’ driver alignment exist.

## Key takeaways
- Uncorrelated sources add in mean-square pressure, giving about three decibels for two equal sources.
- Identical in-phase copies double pressure, giving about six decibels.
- Delayed broadband copies can create comb filtering.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
