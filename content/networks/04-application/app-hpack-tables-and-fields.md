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

**2. An HPACK dynamic table** per connection direction. Fields the encoder chooses to index are added at index **62**, pushing older entries to higher numbers. Both sides charge each entry the same size, so their tables stay identical without any messages about evictions:

```formula reference
E = n + v + 32 B
where
E: the size an entry counts against the dynamic table limit, in bytes (B)
n: the length of the header name, in bytes
v: the length of the header value, in bytes
B: bytes
In words: each stored field costs its name length plus its value length plus a flat 32 bytes of bookkeeping, so short fields cost more table space than their text suggests.
```

When adding an entry would push the total over the limit (default 4,096 bytes), the oldest entries are evicted first. An entry larger than the whole table empties it and is not stored.

**3. Static Huffman coding** for literal strings, with a code tuned to header text. Common characters take 5 or 6 bits.

### Representations

The first bits of each field say what follows:

| Prefix | Meaning |
|---|---|
| `1xxxxxxx` | Indexed: whole field from table |
| `01xxxxxx` | Literal, add to dynamic table |
| `0000xxxx` | Literal, don't index |
| `0001xxxx` | Literal, never index |

So a field already in a table costs one byte while its index is below 127: the top bit is set and the other seven bits hold the index. `:method: GET` (index 2) is `0x82`, and `:scheme: https` (index 7) is `0x87`. A repeated 300-byte cookie that the encoder chose to index can likewise shrink to a byte or two on later requests, as long as it is still in the table.

> [!analogy] Real-world analogy: A shared numbered phrasebook
> Two colleagues on a long radio link each keep an identical notebook. The first time one says a long phrase, both write it down as the newest entry, numbered 62; afterwards the speaker can just say "entry 62". A printed list of common phrases, numbered 1 to 61, came in both notebooks from the start.
>
> **How it maps:** The printed list is the static table, the handwritten entries are the dynamic table, and "entry 62" is an indexed field. Writing a phrase down is a literal with incremental indexing; saying it without writing it down is a literal without indexing.
>
> **Where it stops:** HPACK renumbers as it goes: the newest entry is always 62, so older entries' numbers grow and the oldest drop off the end. Real notebooks could be compared if they disagreed; HPACK decoders cannot. Both sides must process every field block in the same order and evict the same entries, or every later index points at the wrong field. Each direction of a connection also keeps its own separate table.

## Key takeaways
- HPACK shares static and dynamic table state independently in each connection direction.
- Dynamic entries cost their name and value bytes plus 32 bytes, with oldest-entry eviction.

## Further reading
- [RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)
