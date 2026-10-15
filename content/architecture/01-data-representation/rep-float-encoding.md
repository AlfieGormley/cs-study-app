---
id: rep-float-encoding
title: Encoding and decoding binary32
level: intermediate
minutes: 3
summary: Normalise the binary significand before applying the exponent bias.
sourceLesson: rep-floating-point
---

For normal IEEE binary32 values, the stored sign is one bit, the exponent eight bits with bias 127, and the fraction 23 bits with an implicit leading one.

## Worked example: encoding −6.25 as a float

1. Sign: negative, so **1**.
2. Binary: 6.25 = `110.01`.
3. Normalise: `1.1001 × 2²`.
4. Exponent: 2 + 127 = 129 = **`10000001`**.
5. Fraction: the bits after the point, `1001`, padded to 23 bits.

```
1 10000001 10010000000000000000000
```

Group into hex:

```
1100 0000 1100 1000 0000 ... 0000
   C    0    C    8    0 0 0 0
= 0xC0C80000
```

Check it by decoding with the value formula:

```formula
v = (−1)^s (1.f) 2^{e − bias}
v = (−1)^1 × 1.1001_2 × 2^{129 − 127}
v = −1 × 1.5625 × 4 = −6.25
where
v: the value the bits represent
s: the sign bit, here 1 (negative)
1.f: the significand, here 1.1001 in binary = 1 + 1/2 + 1/16 = 1.5625
1.1001_2: the digits 1.1001 read in base 2
f: the stored fraction bits, here 1001 followed by zeros
e: the stored exponent field, here 129
bias: 127 for a float
In words: the bits decode back to −1.5625 × 4, which is −6.25.
```

You can also check it in Python:

```python
# Choose big-endian IEEE binary32 bytes.
import struct
struct.pack('>f', -6.25).hex()
# 'c0c80000'
```

### Decoding works backwards

Take `0x41580000`:

```
0100 0001 0101 1000 0000 ...
0 10000010 10110000000000000000000
```

- Sign 0: positive.
- Exponent `10000010` = 130, so the true exponent is 130 − 127 = 3.
- Significand: 1 followed by the fraction bits `1011`.

```formula
v = (−1)^s (1.f) 2^{e − bias}
v = (−1)^0 × 1.1011_2 × 2^{130 − 127}
v = 1 × 1.6875 × 2^3
v = 1.6875 × 8 = 13.5
where
v: the value the bits represent
s: the sign bit, here 0 (positive)
1.f: the significand; here 1.1011 in binary
1.1011_2: 1 + 1/2 + 1/8 + 1/16 = 1.6875
f: the stored fraction bits, here 1011 followed by zeros
e: the stored exponent field, here 130
bias: 127 for a float
2^3: 2 to the power 3, which is 8
In words: 1.6875 with its binary point moved three places right is 13.5.
```

## Key takeaways
- Normalise the binary significand before applying the exponent bias.
- Interpret the field layout in reverse to decode a finite normal value.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
