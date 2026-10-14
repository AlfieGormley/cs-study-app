---
id: snd-integer-quantisation
title: Integer levels and rounding error
level: intermediate
minutes: 3
summary: Count sample levels and calculate quantisation steps while distinguishing rounding from clipping.
sourceLesson: snd-sampling
---

## Bit depth and quantisation

Each sample must be stored with finite precision. Every extra bit doubles the number of patterns, so with **N bits** a signed integer sample has this many possible values:

```formula
L = 2^N
L = 2^16 = 65536
where
L: the number of distinct levels (values) a sample can take
N: the bit depth, the number of bits per sample; here 16
2^N: 2 raised to the power N (N copies of 2 multiplied together)
In words: each bit doubles the number of levels, so 16 bits give 65,536 of them.
```

| Bits | Levels | Integer range |
|---|---|---|
| 8 | 256 | −128 to 127 |
| 16 | 65,536 | −32,768 to 32,767 |
| 24 | 16,777,216 | −8,388,608 to 8,388,607 |

Rounding the true value to the nearest level is **quantisation**. The levels are evenly spaced, so the step size is the width of the range divided by the number of levels, and rounding to the nearest level is wrong by at most half a step either way:

```formula
Δ = 2 / 2^N
Δ = 2 / 65536 ≈ 0.0000305
e_max = Δ / 2 ≈ 0.0000153
where
Δ: delta, the quantisation step size: the gap between neighbouring levels, in full-scale units
2: the width of the range from −1 to +1 (full scale)
N: the bit depth, in bits; here 16
e_max: the largest possible rounding error when rounding to the nearest level
≈: approximately equal to (rounded)
In words: 16 bits split the range −1 to +1 into steps of about 0.00003, and rounding is never more than half a step out.
```

This assumes the signal stays inside full scale; a value beyond the top or bottom level is clipped, and its error can be much larger.

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
