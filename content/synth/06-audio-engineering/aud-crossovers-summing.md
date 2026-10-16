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

Crossover levels are quoted in decibels, which come from the voltage (amplitude) ratio. These are the numbers you'll meet below:

```formula
L = 20 log_10(A)
20 log_10(0.707) ≈ −3 dB
20 log_10(0.5) ≈ −6 dB
20 log_10(1) = 0 dB
20 log_10(1.414) ≈ +3 dB
where
L: the level change, in decibels (dB); negative means quieter
A: the amplitude ratio, output voltage divided by input voltage (no unit); 1 means unchanged, 0.5 means half
log_10: the base-10 logarithm, which asks "10 to what power gives this number?"
≈: approximately equal to (rounded)
dB: decibel, the unit of level ratio
In words: half the voltage is −6 dB, about 71 % of it (1/√2) is −3 dB, and 1.414 times (√2) is +3 dB.
```

### First order

A first-order low-pass and high-pass at the same frequency are each −3 dB at the crossover, and they sum *exactly* to the input. Filter designers write a filter as a fraction of the input using the variable *s*:

```formula
LP = 1 / (1 + s)
HP = s / (1 + s)
LP + HP = (1 + s) / (1 + s) = 1
where
LP: the low-pass output as a fraction of the input (its transfer function); no unit
HP: the high-pass output as a fraction of the input; no unit
s: the normalised complex frequency (the Laplace variable). For a steady sine wave it equals j times the frequency divided by the crossover frequency, where j is the imaginary unit (the square root of −1) that tracks phase. At the crossover the normalised variable equals the imaginary unit
In words: the low-pass and high-pass pieces share the same bottom line, so their tops add up to that bottom line and the sum is exactly the input, at every frequency.
```

At the crossover, each output's size is about 0.707 of the input (−3 dB), but the two are 90° apart in phase, which is why two 0.707s can still add up to exactly 1. The catch: the two outputs are 90° apart at the crossover, the 6 dB/octave slopes give the drivers a lot of out-of-band signal to handle, and the perfect sum only holds on one axis with ideal drivers.

### Butterworth

A Butterworth filter is maximally flat in its passband and −3 dB at its corner. For a **second-order Butterworth** crossover, the low-pass and high-pass outputs are 180° apart at the crossover, so:

- Wired with the same polarity, they **cancel**: a deep notch at the crossover.
- With one driver's polarity reversed, they sum with a **+3 dB peak** at the crossover (two −3 dB outputs adding in phase).

```formula
A_sum = A_LP + A_HP
A_sum = 0.707 + 0.707 = 1.414
L_sum = 20 log_10(1.414) ≈ +3 dB
where
A_sum: the size of the summed output at the crossover, as a fraction of the input (no unit)
A_LP: the low-pass output's size at the crossover; 0.707 (−3 dB) for a Butterworth
A_HP: the high-pass output's size at the crossover; also 0.707
L_sum: the summed level, in decibels (dB)
log_10: the base-10 logarithm
≈: approximately equal to
dB: decibel, the unit of level ratio
In words: two outputs that are each 71 % of the input, added in step, give 141 % of the input: a 3 dB bump.
```

This simple addition only works because, with one polarity flipped, the two outputs are exactly in step at the crossover.

## Key takeaways
- At a crossover both driver outputs contribute.
- A matched first-order pair sums exactly in the ideal aligned model.
- A second-order Butterworth pair needs a polarity choice and does not give a flat magnitude sum.

## Further reading
- [Crossovers — Linkwitz Lab](https://www.linkwitzlab.com/crossovers.htm)
- [Linkwitz–Riley crossover primer — Rane](https://www.ranecommercial.com/legacy/note160.html)
- [Filter circuits — Linkwitz Lab](https://linkwitzlab.com/filters.htm)
