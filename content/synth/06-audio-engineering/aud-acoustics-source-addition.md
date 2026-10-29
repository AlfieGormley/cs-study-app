---
id: aud-acoustics-source-addition
title: Combine unrelated and coherent sources
level: basic
minutes: 4
summary: Uncorrelated sources add in mean-square pressure, giving about three decibels for two equal sources.
sourceLesson: aud-acoustics
---

## Adding sources

When two sources play at once, how much louder does it get? The answer depends on whether the two waveforms are related.

**Unrelated (incoherent) sources.** Independent sources, such as two air-conditioning units, two singers or a synth and the room's background noise, have waveforms with no fixed relationship. Over a long enough averaging time their peaks sometimes line up and sometimes cancel, and the cross-term averages to zero. What adds is their **mean-square pressure**, which is proportional to power, not their pressures. To combine levels, convert each one back into a relative power, add those powers and convert the total back into decibels:

```formula reference
L_total = 10 log_10(Σ 10^{L_i / 10})
where
L_total: the combined level at the listening position, in dB SPL
L_i: the level of source number i on its own, at the same position, in dB SPL
i: a counter that runs over the sources: 1, 2, 3 and so on
10^{L_i / 10}: the relative power of source i (10 raised to the power of its level divided by 10)
Σ: sigma, "sum of": add up the term for every source
log_10: the base-10 logarithm
In words: Turn each level back into a relative power, add the powers and turn the total back into decibels; decibels themselves never add directly.
```

The useful results:

- Two equal unrelated sources: **+3 dB** (twice the power).
- Four equal unrelated sources: **+6 dB**.
- A source 10 dB quieter than another adds only about **0.4 dB**. The loud one dominates the total, although the quieter one may still be audible if it occupies different frequencies or moments.

**Coherent sources** are different. Two speakers playing the *same* signal add in **pressure**, because their waveforms have a fixed relationship. Where the two arrivals are in phase, the pressure doubles: up to **+6 dB**. Where they arrive half a cycle apart, they cancel deeply.

| Two equal sources | What adds | Best-case change |
|---|---|---|
| Unrelated | power | about +3 dB |
| Identical, in phase | pressure | about +6 dB |
| Identical, half a cycle apart | pressure | deep cancellation |

Whether two copies are in phase depends on the difference in path length compared with the wavelength, so it changes with frequency and listening position. For delayed broadband copies, the repeating frequency peaks and notches are **comb filtering**; a single tone instead shows spatial interference. This is why the microphone lessons' 3:1 rule and the crossover lessons' driver alignment exist.

> [!analogy] Real-world analogy: pushing a swing
> Two people push a child on a swing. If they push together at exactly the right moment each time, every shove adds and the swing goes much higher. If one pushes forwards while the other pulls back, they cancel out. If they each push at random moments, sometimes helping and sometimes fighting, the swing still gains energy on average, but much less dramatically.
>
> **How it maps:** Pushers in step are coherent, in-phase sources whose pressures add (+6 dB). Pushers fighting each other are coherent sources half a cycle apart, which cancel. Random pushers are unrelated sources: only their average energy adds (+3 dB).
>
> **Where it stops:** A swing has one natural rhythm and one position. Sound covers many frequencies, and the phase relationship between two speakers changes with frequency and with where you stand, so the same pair can reinforce in one seat and cancel in the next.

## Key takeaways
- Uncorrelated sources add in mean-square pressure, giving about three decibels for two equal sources.
- Identical in-phase copies double pressure, giving about six decibels.
- Delayed broadband copies can create comb filtering.

## Further reading
- [Wave motion — Dan Russell, Penn State](https://www.acs.psu.edu/drussell/Demos/waves/wavemotion.html)
- [Sound intensity and decibels — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/intens.html)
- [Speed of sound — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Sound/souspe.html)
- [Inverse square law — HyperPhysics, Georgia State](http://hyperphysics.phy-astr.gsu.edu/hbase/Acoustic/invsqs.html)
