---
id: rep-decimal-rounding
title: Decimal fractions and nearest-even rounding
level: intermediate
minutes: 3
summary: A finite binary format rounds repeating decimal fractions.
sourceLesson: rep-floating-point
---

Rounding happens when a value enters a finite binary format and can happen again after each arithmetic operation. A short decimal spelling does not guarantee an exact binary value.

## Why 0.1 + 0.2 != 0.3

The binary-fraction unit showed that 0.1 in binary is `0.000110011001100...`, repeating forever. A binary32 value has only 24 significant bits, so storing one tenth requires rounding. Its stored value is slightly above one tenth; binary64 gives a closer approximation but is still inexact.

On the usual Python platform using IEEE binary64 and nearest-even rounding, each of 0.1, 0.2 and 0.3 is rounded to a nearby representable value. Adding the first two rounds again, and that result differs from the stored 0.3:

```python
# Observe rounded binary64 arithmetic.
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

This is not a bug in Python, or JavaScript, or your CPU. It is the correct IEEE 754 result: the sum of the two nearest doubles, rounded to the nearest double, which happens to be the one just above 0.3's nearest double.

## Rounding

IEEE 754's default rounding mode is **round to nearest, ties to even**. When a result is exactly halfway between two representable values, it picks the one whose last bit is 0. This avoids the upward bias of always rounding halves up.

Python's `round()` uses the same rule for halfway cases: `round(0.5)` is 0, `round(1.5)` is 2, `round(2.5)` is 2. But `round(2.675, 2)` gives 2.67, not because of ties-to-even, but because the stored binary value is slightly below decimal 2.675, so this is not an exact halfway case.

## Key takeaways
- A finite binary format rounds repeating decimal fractions.
- Nearest-even resolves halfway cases using the last retained bit.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
