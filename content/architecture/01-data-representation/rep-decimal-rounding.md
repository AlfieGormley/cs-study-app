---
id: rep-decimal-rounding
title: Decimal fractions and nearest-even rounding
level: intermediate
minutes: 3
summary: A finite binary format rounds repeating decimal fractions.
sourceLesson: rep-floating-point
---

This unit continues the preceding material on binary floating-point representations.

## Why 0.1 + 0.2 != 0.3

The binary-fraction unit showed that 0.1 in binary is `0.000110011001100...`, repeating forever. A float must cut it off after 24 significant bits and round:

```
0.1 as float:
0 01111011 10011001100110011001101
= 0x3DCCCCCD
= 0.100000001490116119384765625
```

The last bits `...1100` became `...1101` because the discarded tail was more than half a unit, so it rounded up. As a double, 0.1 is stored as 0.1000000000000000055511151231257827... Each of 0.1, 0.2 and 0.3 is rounded to its nearest double, and the errors do not cancel:

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

Python's `round()` uses the same rule for halfway cases: `round(0.5)` is 0, `round(1.5)` is 2, `round(2.5)` is 2. But `round(2.675, 2)` gives 2.67, not because of ties-to-even, but because 2.675 is actually stored as 2.67499999999999982236431605997495353221893310546875.

## Key takeaways
- A finite binary format rounds repeating decimal fractions.
- Nearest-even resolves halfway cases using the last retained bit.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
