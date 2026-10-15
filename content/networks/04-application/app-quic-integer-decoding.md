---
id: app-quic-integer-decoding
title: "Decoding QUIC variable-length integers"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "QUIC varints use two length bits followed by a big-endian integer in one, two, four or eight bytes."
---

QUIC frames carry fields such as stream IDs and byte counts. Many fields use the variable-length integer format defined in RFC 9000; its length marker differs from HPACK continuation bits.

### Variable-length integers

QUIC encodes most numbers as **varints**. The top two bits of the first byte give the total length:

| Bits | Bytes | Max value |
|---|---|---|
| 00 | 1 | 63 |
| 01 | 2 | 16,383 |
| 10 | 4 | ~1.07 billion |
| 11 | 8 | ~4.6 quintillion |

Each maximum comes from the bits left once the two length bits are removed:

```formula
V_max = 2^{8n − 2} − 1
V_1 = 2^6 − 1 = 63
V_2 = 2^14 − 1 = 16,383
V_4 = 2^30 − 1 = 1,073,741,823
V_8 = 2^62 − 1 ≈ 4.6 × 10^18
where
V_max: the largest value a varint of n bytes can hold
n: the total length of the varint in bytes: 1, 2, 4 or 8
V_1, V_2, V_4, V_8: V_max for 1, 2, 4 and 8 bytes
^: "to the power of": 2^6 means 6 copies of 2 multiplied together; 10^18 is 1 followed by 18 zeros (a quintillion)
≈: approximately equal to
In words: a varint of n bytes has 8n bits, two of which give the length, so it holds up to 2 to the power (8n − 2), minus one.
```

Except where a field imposes its own shortest-encoding rule, QUIC varints need not use the shortest representation. For example, 37 can be the one byte `25` or the two bytes `40 25`. QUIC frame-type fields require the shortest form.

To decode, take the first byte, clear its top two bits (AND with `0x3F`), then append each following byte as the next 8 bits. For `7b bd`, the top bits `01` say 2 bytes:

```formula
v = 256(b_0 − 0x40) + b_1
v = (0x7b − 0x40) × 256 + 0xbd
v = 59 × 256 + 189 = 15,293
where
v: the decoded value
b_0: the first byte, 0x7b in hexadecimal (base 16, prefix 0x), which is 7 × 16 + 11 = 123; subtracting 0x40 (64) removes the length bits 01
b_1: the second byte, 0xbd = 11 × 16 + 13 = 189
In words: strip the two length bits from the first byte, then treat the two bytes as one big-endian number.
```

```python
def varint(data):
    if not data:
        raise ValueError("empty varint")
    # Top bits select 1, 2, 4 or 8 bytes.
    length = 1 << (data[0] >> 6)
    if len(data) < length:
        raise ValueError("truncated varint")
    # Remove the two length bits.
    v = data[0] & 0x3F
    for b in data[1:length]:
        # Append the next big-endian byte.
        v = (v << 8) | b
    return v, length

print(varint(bytes.fromhex("25")))
# (37, 1)
print(varint(bytes.fromhex("7bbd")))
# (15293, 2)
```

## Key takeaways
- QUIC varints use two length bits followed by a big-endian integer in one, two, four or eight bytes.
- A decoder must check the available length before consuming the selected representation.

## Further reading
- [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)
