---
id: app-http-chunk-decoding
title: "Streaming bodies with chunked encoding"
level: basic
minutes: 4
sourceLesson: app-http-wire
summary: "Chunk sizes are hexadecimal byte counts; their CRLF delimiters are framing rather than content."
---

## Chunked transfer encoding

`Content-Length` must be known *before* the first body byte is sent. That is a problem for anything generated on the fly: a streamed template, a database export, a proxied upstream, a long-poll. Without a length, the server could only signal the end by closing the connection, losing persistence.

**Chunked encoding** solves this. The body is sent as a sequence of chunks, each prefixed by its size in **hexadecimal**, and a zero-size chunk marks the end:

```
HTTP/1.1 200 OK\r\n
Transfer-Encoding: chunked\r\n
\r\n
7\r\n
Mozilla\r\n
11\r\n
Developer Network\r\n
0\r\n
\r\n
```

`11` is hex, so that chunk is 17 bytes ("Developer Network"). In hexadecimal each digit is worth 16 times the digit to its right, so converting a chunk-size line to an ordinary decimal byte count works like this:

```formula
S = d_1 × 16 + d_0
S = 1 × 16 + 1 = 17 B
L = S_1 + S_2 = 7 B + 17 B = 24 B
where
S: the chunk size in bytes, as an ordinary decimal number
d_1: the left (sixteens) digit of a two-digit hexadecimal size line; here 1
d_0: the right (units) digit; here 1. The hex digits A to F stand for 10 to 15
S_1: the size of the first chunk, hex 7 = 7 bytes ("Mozilla")
S_2: the size of the second chunk, hex 11 = 17 bytes ("Developer Network")
L: the length of the decoded body in bytes
B: bytes
In words: the size line "11" means one sixteen plus one, so 17 bytes; the two chunks together give a 24-byte body.
```

The decoded body is `MozillaDeveloper Network`, 24 bytes. The CRLF after each chunk's data is framing, not content, so it is not counted. Reading `11` as decimal eleven would cut the chunk short and desynchronise the parser.

A deliberately restricted decoder for an already-buffered, bounded message with **no extensions or trailers**. It rejects those unsupported forms and returns any following bytes separately. Production receivers must handle the full grammar and incremental input.

```python
import re

def read_chunked(buf):
    if len(buf) > 1_000_000:
        raise ValueError("demo limit")
    parts = []
    while True:
        # Remove the next size line.
        line, sep, buf = buf.partition(
            b"\r\n")
        if not sep or not re.fullmatch(
                rb"[0-9A-Fa-f]+", line):
            raise ValueError("bad size")
        # Sizes are hex, not decimal.
        size = int(line, 16)
        if size == 0:
            if not buf.startswith(b"\r\n"):
                raise ValueError(
                    "bad terminator")
            # Keep any next-message bytes.
            return b"".join(parts), buf[2:]
        if (len(buf) < size + 2
                or buf[size:size + 2]
                != b"\r\n"):
            raise ValueError("bad chunk")
        # Save data; skip its trailing CRLF.
        parts.append(buf[:size])
        buf = buf[size + 2:]
```

Details worth knowing:

- **Trailer fields.** After the `0` chunk, the sender may add header fields before the final blank line, for example a checksum computed while streaming. Native gRPC over HTTP/2 relies on trailers to send its status. Many HTTP/1.1 clients and browsers ignore them.
- **Chunk extensions** (`7;name=value`) can carry per-chunk metadata. A conforming receiver ignores unrecognised extensions after parsing their syntax and imposing suitable limits.
- Chunks have nothing to do with TCP segments. A 7-byte chunk may arrive split across two `recv` calls, and ten chunks may arrive in one. A real parser is a finite-state machine fed arbitrary slices.
- HTTP/2 and HTTP/3 **forbid** `Transfer-Encoding`. Both have length-delimited DATA frames. HTTP/2 signals message completion with END_STREAM; HTTP/3 uses the end of its underlying QUIC stream, not a DATA-frame END_STREAM flag.

## Key takeaways
- Chunk sizes are hexadecimal byte counts; their CRLF delimiters are framing rather than content.
- A restricted buffered decoder demonstrates the rules but is not a production incremental parser.

## Further reading
- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112)
- [RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)
