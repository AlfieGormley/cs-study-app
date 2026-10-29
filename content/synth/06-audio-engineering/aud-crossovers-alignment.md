---
id: aud-crossovers-alignment
title: Align drivers and protect the tweeter
level: advanced
minutes: 4
summary: Distance offsets create frequency-dependent phase error.
sourceLesson: aud-crossovers
---

## Driver offset and phase

The preceding lessons’ ideal sums assume both drivers' sound starts from the same point. Real drivers don't: a woofer's **acoustic centre** usually sits further back than a tweeter's on a flat baffle. A path difference becomes a time delay (sound covers about 3.4 mm every 10 µs), and a fixed time delay becomes a phase error that **grows with frequency**, because the same delay is a bigger slice of a shorter cycle.

```formula reference
φ = 360° f d / c
where
φ: the phase error the offset causes, in degrees (°); 360° is one whole cycle
f: the frequency in question, in hertz (Hz)
d: the path difference: how much further one acoustic centre is from the listener, in metres (m)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
Hz: hertz, cycles per second
In words: The offset's delay is the path difference divided by the speed of sound, and that delay is a larger fraction of a cycle at higher frequencies, so the phase error grows in proportion to frequency.
```

For example, an 8 cm offset is about 233 µs, almost half of a 2 kHz cycle (500 µs): close to 180° at the crossover, where both drivers contribute equally. A 2 cm offset is about 58 µs, roughly 40° at 2 kHz.

Modelling an ideal 2 kHz LR4 crossover with the woofer's sound arriving late shows the effect on the on-axis sum:

| Frequency | Aligned | Woofer 2 cm behind | Woofer 8 cm behind |
|---|---|---|---|
| 1 kHz | 0 dB | 0 dB | −0.5 dB |
| 1.5 kHz | 0 dB | −0.2 dB | −3.8 dB |
| 2 kHz | 0 dB | −0.6 dB | −19.6 dB |
| 2.5 kHz | 0 dB | −0.8 dB | −6.4 dB |
| 4 kHz | 0 dB | −0.5 dB | 0 dB |

With the woofer 2 cm behind, the dip is under 1 dB. At 8 cm there's a deep on-axis hole at the crossover, because the two equal outputs arrive almost half a cycle apart. Remedies:

- **DSP delay** on the earlier driver (easy in active/DSP systems).
- **Stepped or sloped baffles** to line up acoustic centres physically.
- Choosing the crossover frequency and filter shapes so the *acoustic* responses (filter × driver) hit the target, and checking the result by measurement.

Even when on-axis is perfect, moving up or down changes the path lengths to the two drivers. That's **lobing**: the summed response changes with vertical angle. LR crossovers with aligned drivers keep the main radiation lobe pointing straight ahead, which is one reason they're popular.

## Filter choice also protects a driver

The first-order and LR4 filters from the preceding lessons pass very different amounts of signal below the crossover. At half the crossover frequency (one octave below), the ideal first-order high-pass is only about 7 dB down, while LR4 is about 25 dB down. That octave is often where a small dome tweeter's own resonance sits, where it has little excursion to spare.

This reduces the tweeter’s out-of-band input for the same source level. It does not establish a safe crossover or power rating: use the exact driver’s recommended filter type, minimum crossover and excursion and thermal limits, then measure the acoustic result.

## Key takeaways
- Distance offsets create frequency-dependent phase error.
- Delay or physical alignment can improve the target-axis sum.
- Steeper high-pass attenuation reduces out-of-band tweeter input but does not establish safe operating power.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
