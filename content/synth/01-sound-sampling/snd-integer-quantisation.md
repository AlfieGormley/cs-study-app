---
id: snd-integer-quantisation
title: Integer levels and rounding error
level: intermediate
minutes: 3
summary: Explain how bit depth changes level spacing and distinguish rounding error from clipping.
sourceLesson: snd-sampling
---

## Bit depth and quantisation

Each sample must be stored with finite precision. Every extra bit doubles the number of patterns available to represent a sample.

For example, 16 bits provide 65,536 distinct levels. A signed sample uses some codes for negative values, one for zero and the rest for positive values; it does not lose half its precision by being signed.

| Bits | Levels | Integer range |
|---|---|---|
| 8 | 256 | −128 to 127 |
| 16 | 65,536 | −32,768 to 32,767 |
| 24 | 16,777,216 | −8,388,608 to 8,388,607 |

Rounding the true value to the nearest level is **quantisation**. The levels are evenly spaced, so the step size is the width of the range divided by the number of levels, and rounding to the nearest level is wrong by at most half a step either way:

```formula reference
Δ = 2 / 2^N
e_max = Δ / 2
where
Δ: delta, the quantisation step size: the gap between neighbouring levels, in full-scale units
2: the width of the range from −1 to +1 (full scale)
N: the bit depth, in bits; here 16
e_max: the largest possible rounding error when rounding to the nearest level
In words: For signed samples scaled around minus one to plus one, each extra bit halves the gap between levels. Nearest rounding stays within half a gap when the signal does not overload.
```

This assumes the signal stays inside full scale; a value beyond the top or bottom level is clipped, and its error can be much larger.

> [!analogy] Real-world analogy: Rounding a length to ruler marks
> A ruler with finer marks lets you report a length more closely. Rounding to the nearest mark moves the report by no more than half the gap between marks.
>
> **How it maps:** Ruler marks are integer sample levels; adding a bit makes the marks twice as dense across the same full-scale range. Nearest rounding chooses the closest available level.
>
> **Where it stops:** An audio sample can be negative, and its signed endpoints are asymmetric. Values beyond the available range overload rather than simply rounding to a nearby internal mark.

## Pitfalls

- **Truncating instead of rounding.** Truncation toward zero gives sign-dependent error approaching a full step; it need not add DC to a symmetric signal. Rounding downward instead has a negative bias, averaging about half a step under the uniform-error model. Nearest rounding limits error to half a step away from overload.

## Key takeaways

- Each extra bit doubles the number of distinct integer sample values.
- Nearest rounding stays within half a step away from overload.
- Signed integer endpoints are asymmetric; overload and truncation require separate care.

## Further reading

- [Quantization (signal processing) — Wikipedia](https://en.wikipedia.org/wiki/Quantization_(signal_processing))
- [Audio bit depth — Wikipedia](https://en.wikipedia.org/wiki/Audio_bit_depth)
- [Taking The Mystery Out of the Infamous Formula "SNR = 6.02N + 1.76dB" — Analog Devices MT-001](https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf)
