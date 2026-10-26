---
id: rep-float-encoding
title: Encoding and decoding binary32
level: intermediate
minutes: 3
summary: Normalise the binary significand before applying the exponent bias.
sourceLesson: rep-floating-point
---

A binary32 decoder must identify the fields before doing arithmetic. The sign occupies one bit, the exponent eight bits, and the stored fraction 23 bits. Normal values use exponent bias 127 and an implicit leading one; reserved exponents select different rules.

## Read the fields, then the value

Here is the encoding of −6.25:

```
sign  exponent  fraction
1     10000001  10010000000000000000000
```

- The sign bit says negative.
- Stored exponent 129 means a true exponent of two after removing the bias: scale the significand by four.
- Fraction bits start `1001`. Restore the implicit leading one to get binary `1.1001`, whose value is 1.5625.

Together these fields represent −6.25. The complete encoding is `0xC0C80000`. The sign does not participate in two's-complement negation: flipping that one sign bit gives positive 6.25 while keeping the exponent and fraction.

## Use a decoder to inspect bytes

Python's `struct` module can encode and decode the format directly:

```python
# Explicit big-endian IEEE binary32 bytes.
import struct
struct.pack('>f', -6.25).hex()
# 'c0c80000'
raw = bytes.fromhex('41580000')
struct.unpack('>f', raw)
# (13.5,)
```

The `>` chooses big-endian byte order, and `f` chooses binary32. A hex value from a debugger and a sequence of bytes are not interchangeable without knowing byte order. The later memory-layout units explain that distinction.

## Diagnose a decoding mistake

A decoder that reads the fraction as an integer loses its fractional position weights. A decoder that omits the hidden one makes normal magnitudes too small. A decoder that treats the stored exponent as the true exponent applies a wildly incorrect scale.

Classify the exponent first. With an all-zero exponent, zero and subnormal rules apply; with an all-one exponent, infinity and NaN rules apply. The normal rule cannot decode every bit pattern.

When writing an encoder, first express the magnitude with the binary point after its leading one, record the scale, and store the remaining fraction bits. If they do not fit, rounding is required. Use a tested format implementation for routine conversion; the important skill is recognising which field caused a wrong result.

## Key takeaways
- Decode the field roles before interpreting the value.
- Normal values restore a hidden one and remove the exponent bias.
- Check reserved exponents and byte order before applying the normal rule.

## Further reading
- [Oracle numerical computation guide](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_math.html)
- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html)
