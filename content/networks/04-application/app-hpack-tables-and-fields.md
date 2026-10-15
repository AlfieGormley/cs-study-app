---
id: app-hpack-tables-and-fields
title: "HPACK tables and indexed fields"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "HPACK shares static and dynamic table state independently in each connection direction."
---

## HPACK: header compression

HTTP/1.1 headers repeat on every request: the same `user-agent`, `accept` and cookies, hundreds of bytes each time. HPACK ([RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)) compresses them using three tools.

**1. An HPACK static table** of 61 common fields, numbered from 1:

| Index | Name | Value |
|---|---|---|
| 1 | :authority | |
| 2 | :method | GET |
| 3 | :method | POST |
| 4 | :path | / |
| 6 | :scheme | http |
| 7 | :scheme | https |
| 8 | :status | 200 |

**2. An HPACK dynamic table** per connection direction. Fields the encoder chooses to index are added at index **62**, pushing older entries to higher numbers. Each entry is charged a fixed overhead on top of its text, so both sides measure the table's usage the same way:

```formula
E = n + v + 32 B
where
E: the size an entry counts against the dynamic table limit, in bytes (B)
n: the length of the header name, in bytes
v: the length of the header value, in bytes
B: bytes
In words: an entry costs its name plus its value plus a flat 32 bytes of bookkeeping overhead.
```

When adding an entry would push the total over the limit (default 4,096 bytes), the oldest entries are evicted first.

**3. Static Huffman coding** for literal strings, with a code tuned to header text. Common characters take 5 or 6 bits.

### Representations

The first bits of each field say what follows:

| Prefix | Meaning |
|---|---|
| `1xxxxxxx` | Indexed: whole field from table |
| `01xxxxxx` | Literal, add to dynamic table |
| `0000xxxx` | Literal, don't index |
| `0001xxxx` | Literal, never index |

So `:method: GET` is one byte, `1` followed by index 2 in 7 bits. The leading 1 bit is worth 128, so the byte is 128 plus the index:

```formula
x = 128 + i
x = 128 + 2 = 130 = 0x82
where
x: the value of the single byte that encodes an indexed field for table indices below 127; larger indices need continuation bytes. The result is written in hexadecimal (base 16, marked by the prefix 0x): 0x82 means 8 × 16 + 2 = 130
i: the field's index in the table; 2 for :method: GET
In words: an indexed field is one byte whose top bit is set and whose other seven bits hold the index.
```

By the same rule, `:scheme: https` (index 7) is `0x87`.

## Key takeaways
- HPACK shares static and dynamic table state independently in each connection direction.
- Dynamic entries cost their name and value bytes plus 32 bytes, with oldest-entry eviction.

## Further reading
- [RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)
