---
id: rep-float-spacing
title: Precision, spacing and lost increments
level: intermediate
minutes: 4
summary: Spacing doubles between successive normal binades.
sourceLesson: rep-floating-point
---

Assume nearest-even binary32 or binary64 arithmetic: halfway results go to the representable value whose last retained bit is zero.

## Precision and range

The significand has a fixed number of bits, so the **gap between neighbouring floats grows** with their size. Floats are dense near zero and sparse far away.

The table uses scientific notation: the e suffix introduces a decimal exponent. For example, an exponent of negative seven scales the preceding digits by one ten-millionth.

| | float | double |
|---|---|---|
| Significant bits | 24 | 53 |
| Decimal digits | about 7 | about 15–16 |
| Machine epsilon | about 1.19e−7 | about 2.22e−16 |
| Largest | ≈ 3.40e38 | ≈ 1.80e308 |
| Consecutive exact integers through | 16,777,216 | 9,007,199,254,740,992 |

**Machine epsilon** is the gap between 1.0 and the next float above it. More significant bits make that gap smaller. It is a precision measure near one, not a universal absolute error tolerance.

For normal finite values with a next finite neighbour further from zero, the gap scales with the size of the number. It is constant within each **binade** (the range from one power of two up to the next) and doubles at each power of two:

```formula reference
Δ = 2^E ε   for 2^E ≤ |x| < 2^{E+1}
where
Δ: delta, the gap between x and the next representable value further from zero
x: a normal floating-point value with a next finite neighbour further from zero
|x|: the absolute value of x: x without its sign
E: the true exponent of x: the power of two at or just below |x|
ε: machine epsilon, 2^{−23} for float and 2^{−52} for double
≤: less than or equal to; <: less than
In words: normal floating-point spacing is constant between successive powers of two and doubles in the next such interval. Near 16,777,216, binary32 values are two apart.
```

Subnormals have fixed absolute spacing. Two consequences:

- Above 16,777,216 a binary32 value cannot represent every integer. `16777217.0f` rounds to 16,777,216. Using a `float` for a counter or a timestamp silently stops counting.
- Above 9,007,199,254,740,992 a double cannot either. That is why JavaScript Number values (binary64, distinct from BigInt) have `Number.MAX_SAFE_INTEGER`, one less than that boundary (9,007,199,254,740,991); decimal strings or BigInt are alternatives for larger exact integer IDs.

Adding a small number to a big one can lose it entirely:

```python
# The unit increment rounds away first.
>>> 1e16 + 1.0 - 1e16
0.0
```

Near ten thousand million million, neighbouring binary64 values are two apart.

Adding one to ten thousand million million is exactly halfway between two doubles, and nearest-even rounds back to the starting value.

> [!analogy] Real-world analogy: A map at different scales
> A ruler on a local map distinguishes small distances; the same marks on a world map cover much larger distances.
>
> **How it maps:** A fixed number of significand bits supplies a fixed amount of detail while the exponent changes the scale. At larger magnitudes, adjacent representable values are further apart.
>
> **Where it stops:** Normal floats change spacing in power-of-two intervals; subnormals have fixed spacing. This is a representation limit, not uncertainty in the original measurement.

## Key takeaways
- Spacing doubles between successive normal binades.
- A large floating counter can stop responding to unit increments.
- Small additions can disappear before later subtraction.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
