---
id: app-hpack-integers-and-trace
title: "HPACK integer prefixes and a header-block trace"
level: intermediate
minutes: 5
sourceLesson: app-http2-quic
summary: "HPACK fills a bit prefix, then sends any remainder in little-endian seven-bit groups."
---

HPACK compresses HTTP/2 fields using shared tables. The static table has 61 entries; newly indexed dynamic fields start at 62. An indexed representation sets its top bit, while a literal representation carries a name or name index and a value. This unit follows the integer encoding and one complete field block.

Integers use an **N-bit prefix**: the first byte has a few bits left over for the number (5 bits in the example below; the RFC calls this count N). If the value is smaller than the all-ones pattern of those bits, it is stored directly in them. Otherwise the prefix is set to all ones and the remainder follows in 7-bit groups, least significant first, with the top bit meaning "more follows". For 1337 with a 5-bit prefix:

```formula
P = 2^N − 1 = 2^5 − 1 = 31
r = 1337 − 31 = 1306
1306 = 10 × 128 + 26
b_1 = 26 + 128 = 154
b_2 = 10
where
P: the largest value the N-bit prefix can hold, used as the "more bytes follow" marker
N: the number of prefix bits available in the first byte; here 5
^: "to the power of": 2^5 means 5 copies of 2 multiplied together, which is 32
r: the remainder still to encode after the prefix is filled
b_1: the first continuation byte: the low 7 bits of r (26), plus 128 because more bytes follow
b_2: the last continuation byte: the remaining high part of r (10), with no 128 added because nothing follows
In words: 1337 does not fit in 5 bits, so the prefix is set to 31 and the leftover 1306 is sent as 26-with-a-continue-flag (154) then 10.
```

The decoder reverses this: 31 + 26 + 10 × 128 = 1337. The same integer-prefix algorithm in Python:

```python
def enc_int(value, n):
    if (type(value) is not int or value < 0
            or type(n) is not int
            or not 1 <= n <= 8):
        raise ValueError("bad integer")
    # All ones marks continuation.
    limit = (1 << n) - 1
    if value < limit:
        return [value]
    out = [limit]
    # Only encode the remaining value.
    value -= limit
    # Emit low groups with a continue bit.
    while value >= 128:
        out.append(value % 128 + 128)
        value //= 128
    # The final group has no continue bit.
    out.append(value)
    return out

print(enc_int(10, 5))    # [10]
print(enc_int(1337, 5))  # [31, 154, 10]
```

### Decoding a real header block

The first request in RFC 7541's examples is:

```
82 86 84 41 0f 77 77 77 2e 65 78
61 6d 70 6c 65 2e 63 6f 6d
```

1. `82`: indexed 2, `:method: GET`.
2. `86`: indexed 6, `:scheme: http`.
3. `84`: indexed 4, `:path: /`.
4. `41` = `01 000001`: literal with indexing, name from index 1 (`:authority`).
5. `0f`: a 15-byte string, not Huffman-coded (top bit 0): `www.example.com`.

The decoder adds `:authority: www.example.com` to the dynamic table at index 62. Its size and the cost of reusing it work out as:

```formula
E = n + v + 32 B
E = 10 B + 15 B + 32 B = 57 B
x = 128 + 62 = 190 = 0xbe
F = 1 B + 1 B + 15 B = 17 B
where
E: the entry's size against the table limit, in bytes (B)
n: the name length; ":authority" is 10 bytes
v: the value length; "www.example.com" is 15 bytes
x: the one-byte indexed representation that later refers to index 62. In hexadecimal (base 16, prefix 0x) it is written 0xbe: b is 11 and e is 14, so 11 × 16 + 14 = 190
F: the bytes the original literal field occupied on the wire: the 0x41 representation byte, the 0x0f length byte and the 15-byte value
B: bytes
In words: the entry costs 57 bytes of table space, and once stored, a 17-byte literal can be replaced by the single byte 0xbe.
```

That saving only applies if the entry is still at index 62 and the encoder chooses to reference it.

### Why "never index" exists

The 2012 **CRIME** attack showed that compressing secrets alongside attacker-controlled data leaks the secret through compressed sizes. HPACK resists this because table entries match only whole fields, but an attacker who can inject guesses can still test whether a guessed field value is already in the table. The **never-indexed** form tells every hop, including proxies re-encoding the headers, not to put a value such as a short cookie or `authorization` token in a table.

## Key takeaways
- HPACK fills a bit prefix, then sends any remainder in little-endian seven-bit groups.
- A never-indexed representation tells re-encoding intermediaries to keep the field out of dynamic tables.

## Further reading
- [RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)
