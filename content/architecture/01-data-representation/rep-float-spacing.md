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
| Machine epsilon | 2^−23 ≈ 1.19e−7 | 2^−52 ≈ 2.22e−16 |
| Largest | ≈ 3.40e38 | ≈ 1.80e308 |
| Consecutive exact integers through | 16,777,216 | 9,007,199,254,740,992 |

**Machine epsilon** is the gap between 1.0 and the next float above it. It follows from the number of significant bits:

```formula
ε = 2^{−(p − 1)}
ε = 2^{−23} ≈ 1.19 × 10^{−7}   for p = 24
ε = 2^{−52} ≈ 2.22 × 10^{−16}   for p = 53
where
ε: epsilon, machine epsilon: the gap between 1.0 and the next larger representable value
p: the precision: the number of significant bits, including the hidden bit (24 for float, 53 for double)
2^{−23}: 1 divided by 2 to the power 23, the weight of the last fraction bit when the exponent is 0
≈: approximately equal to (rounded)
In words: the last of the 23 stored fraction bits of a float is worth about 0.000000119 when the number is near 1, so that is the smallest step up from 1.0.
```

For normal finite values with a next finite neighbour further from zero, the gap scales with the size of the number. It is constant within each **binade** (the range from one power of two up to the next) and doubles at each power of two:

```formula
Δ = 2^E ε   for 2^E ≤ |x| < 2^{E+1}
Δ ≈ |x| ε
Δ = 2^24 × 2^{−23} = 2
where
Δ: delta, the gap between x and the next representable value further from zero
x: a normal floating-point value with a next finite neighbour further from zero
|x|: the absolute value of x: x without its sign
E: the true exponent of x: the power of two at or just below |x|
ε: machine epsilon, 2^{−23} for float and 2^{−52} for double; the third line uses a float from 2^24 up to 2^25
≤: less than or equal to; <: less than
≈: approximately equal to
In words: between two neighbouring powers of two the gap is fixed, and it is roughly the size of the number times epsilon, so from 2^24 upwards neighbouring floats are 2 apart.
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

The gap formula explains it:

```formula
2^53 ≤ 10^16 < 2^54
Δ = 2^53 × 2^{−52} = 2
where
2^53: about 9.007 × 10^15, the power of two just below 10^16
2^54: about 1.8 × 10^16, the next power of two
Δ: delta, the gap between neighbouring doubles in this binade
2^{−52}: machine epsilon for a double
≤: less than or equal to; <: less than
In words: 10^16 lies between 2 to the 53 and 2 to the 54, where neighbouring doubles are 2 apart.
```

Adding one to ten thousand million million is exactly halfway between two doubles, and nearest-even rounds back to the starting value.

## Key takeaways
- Spacing doubles between successive normal binades.
- A large floating counter can stop responding to unit increments.
- Small additions can disappear before later subtraction.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
