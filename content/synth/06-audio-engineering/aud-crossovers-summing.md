---
id: aud-crossovers-summing
title: Why crossover phase matters
level: advanced
minutes: 4
summary: At a crossover both driver outputs contribute.
sourceLesson: aud-crossovers
---

## Making the outputs add up

The low-pass and high-pass outputs have to sum to a flat response. Magnitude alone isn't enough: at the crossover frequency both drivers contribute, so their relative **phase shift** decides whether they add or cancel.

Crossover levels are quoted in decibels of voltage (amplitude) ratio. A few landmarks are enough for this lesson:

| Amplitude ratio | Level |
|---|---|
| 1.414 | about +3 dB |
| 1 | 0 dB |
| 0.707 | about −3 dB |
| 0.5 | about −6 dB |

### Phase decides how outputs add

Two outputs add simply only when they are in step. If they are out of step, their sizes combine like two pushes in different directions: two 0.707 outputs a quarter-cycle (90°) apart add to exactly 1, while two 0.707 outputs half a cycle (180°) apart cancel completely.

> [!analogy] Real-world analogy: two people pushing a trolley
> Two people push a heavy trolley. If both push straight ahead, their efforts add fully. If one pushes ahead and the other pushes from the side, the trolley moves diagonally and goes less far forward than the two pushes would add up to. If they push from opposite ends, they cancel.
>
> **How it maps:** Each push is one driver's output. The direction of the push is its phase at that frequency. Pushes in the same direction are in-phase outputs that add fully; at right angles they are 90° apart; head-on they are 180° apart and cancel.
>
> **Where it stops:** Phase is a difference in timing, not a direction in space, and a crossover's phase difference changes with frequency, so the "angle" between the two pushes changes as you sweep through the crossover region.

### First order

A first-order low-pass and high-pass at the same frequency are each −3 dB (0.707) at the crossover, and they are 90° apart there. Like the right-angle pushes, two 0.707s a quarter-cycle apart add to exactly 1. In fact this pair sums *exactly* to the input at every frequency in the ideal model:

```formula reference
LP = 1 / (1 + s)
HP = s / (1 + s)
LP + HP = (1 + s) / (1 + s) = 1
where
LP: the low-pass output as a fraction of the input (its transfer function); no unit
HP: the high-pass output as a fraction of the input; no unit
s: the normalised complex frequency (the Laplace variable). For a steady sine wave it equals j times the frequency divided by the crossover frequency, where j is the imaginary unit (the square root of −1) that tracks phase
In words: A matched first-order low-pass and high-pass share the same denominator, so their sum is exactly the input at every frequency in the ideal model.
```

The catch: the 6 dB/octave slopes give each driver a lot of out-of-band signal to handle, the two outputs are 90° apart, and the perfect sum only holds on one axis with ideal, aligned drivers.

### Butterworth

A Butterworth filter is maximally flat in its passband and −3 dB at its corner. For a **second-order Butterworth** crossover, the low-pass and high-pass outputs are 180° apart at the crossover, so:

- Wired with the same polarity, they **cancel**: a deep notch at the crossover.
- With one driver's polarity reversed, they are back in step and simply add: two 0.707 outputs make 1.414, a **+3 dB peak** at the crossover.

Neither choice is flat, which is the problem the next lesson's Linkwitz–Riley alignment solves.

## Key takeaways
- At a crossover both driver outputs contribute.
- A matched first-order pair sums exactly in the ideal aligned model.
- A second-order Butterworth pair needs a polarity choice and does not give a flat magnitude sum.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
