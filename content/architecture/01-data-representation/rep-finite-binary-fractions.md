---
id: rep-finite-binary-fractions
title: Finite and repeating binary fractions
level: basic
minutes: 3
summary: Fractional binary positions have weights one half, one quarter and so on.
sourceLesson: rep-number-systems
---

This unit continues the preceding material on binary place values.

## Fractions in binary

Positions to the right of the point have weights 1/2, 1/4, 1/8 and so on: the powers of two continue below 1. So `0.101` in binary is:

```formula
0.101_2 = 1 × 2^−1 + 0 × 2^−2 + 1 × 2^−3
0.101_2 = 1/2 + 0 + 1/8 = 0.625
where
0.101_2: the digits 0.101 read in base 2; the small 2 written below the number names the base
2^−1: 2 to the power −1, which means 1/2 = 0.5; a negative power means "1 divided by" the positive power
2^−2: 1/(2 × 2) = 1/4 = 0.25
2^−3: 1/(2 × 2 × 2) = 1/8 = 0.125
In words: the first place after the binary point is worth a half, the next a quarter, the next an eighth; add the ones that hold a 1.
```

To convert a decimal fraction, **multiply by 2** repeatedly and take the integer parts, reading **top to bottom**:

```
0.625 × 2 = 1.25   → 1
0.25  × 2 = 0.5    → 0
0.5   × 2 = 1.0    → 1   (stop: 0 left)
0.625 = 0.101₂
```

Try 0.1 and something unsettling happens:

```
0.1 × 2 = 0.2 → 0
0.2 × 2 = 0.4 → 0
0.4 × 2 = 0.8 → 0
0.8 × 2 = 1.6 → 1
0.6 × 2 = 1.2 → 1
0.2 × 2 = 0.4 → 0   (repeats from here)
0.1 = 0.0001100110011...₂
```

It never terminates, just as 1/3 never terminates in decimal. A fraction terminates in a given base if and only if, after reducing it to lowest terms, every prime factor of its denominator also divides the base. For example, 3/8 has denominator 8 = 2 × 2 × 2, so it ends in binary (`0.011`). Ten is 2 × 5, so 1/10 has a factor of 5 that base 2 cannot express. This is the root of the surprises covered in the floating-point units.

## Key takeaways
- Fractional binary positions have weights one half, one quarter and so on.
- A reduced fraction terminates in binary only when its denominator is a power of two.

## Further reading
- [Python integer conversion functions](https://docs.python.org/3/library/functions.html)
- [NIST binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
