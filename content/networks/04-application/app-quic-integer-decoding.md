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

Each maximum is simply the largest number that fits in the bits left after the two length bits: 6, 14, 30 or 62 bits. Values up to 63, common for small counts and lengths, cost one byte, while the format can still carry very large byte offsets.

Except where a field imposes its own shortest-encoding rule, QUIC varints need not use the shortest representation. For example, 37 can be the one byte `25` or the two bytes `40 25`. QUIC frame-type fields require the shortest form.

To decode, read the top two bits of the first byte to learn the length, clear those two bits (AND with `0x3F`), then append each following byte as the next 8 bits, most significant first. For `7b bd`, the top bits `01` say 2 bytes; clearing them turns `7b` into `3b` (59), and `3b bd` read as one big-endian number is 15,293.

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
