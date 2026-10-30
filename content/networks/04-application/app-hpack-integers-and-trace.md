---
id: app-hpack-integers-and-trace
title: "HPACK integer prefixes and a header-block trace"
level: intermediate
minutes: 5
sourceLesson: app-http2-quic
summary: "HPACK fills a bit prefix, then sends any remainder in little-endian seven-bit groups."
---

HPACK compresses HTTP/2 fields using shared tables. The static table has 61 entries; newly indexed dynamic fields start at 62. An indexed representation sets its top bit, while a literal representation carries a name or name index and a value. This unit follows the integer encoding and one complete field block.

Integers use an **N-bit prefix**: the first byte has a few bits left over for the number (5 bits in the example below; the RFC calls this count N). If the value is smaller than the all-ones pattern of those bits, it is stored directly in them. Otherwise the prefix is set to all ones and the remainder follows in 7-bit groups, least significant first, with the top bit of each byte meaning "more follows".

For 1337 with a 5-bit prefix: five bits hold at most 31, so the prefix is set to 31 (the "more follows" marker) and 1306 remains. Its low seven bits are 26, sent as 154 (26 with the continue bit, worth 128, set); the rest is 10, sent as a final byte without the continue bit. The decoder reverses this: 31, plus 26, plus 10 lots of 128, gives 1337.

The same integer-prefix algorithm in Python:

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

The design keeps small numbers to a single byte, which matters because most indexes and string lengths in a header block are small.

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

The decoder adds `:authority: www.example.com` to the dynamic table at index 62. That entry costs 57 bytes of table space (10 name bytes, 15 value bytes and HPACK's 32-byte overhead). The literal took 17 bytes on the wire (the `41` byte, the `0f` length byte and 15 bytes of text); once stored, a later request can send the single byte `be` (index 62 with the top bit set) instead. That saving applies only while the entry is still at index 62 and the encoder chooses to reference it.

### Why "never index" exists

The 2012 **CRIME** attack showed that compressing secrets alongside attacker-controlled data leaks the secret through compressed sizes. HPACK resists this because table entries match only whole fields, but an attacker who can inject guesses can still test whether a guessed field value is already in the table. The **never-indexed** form tells every hop, including proxies re-encoding the headers, not to put a value such as a short cookie or `authorization` token in a table.

## Key takeaways
- HPACK fills a bit prefix, then sends any remainder in little-endian seven-bit groups.
- A never-indexed representation tells re-encoding intermediaries to keep the field out of dynamic tables.

## Further reading
- [RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)
