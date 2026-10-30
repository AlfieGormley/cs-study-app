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

`11` is hexadecimal: one sixteen plus one, so that chunk is 17 bytes ("Developer Network"). The decoded body is `MozillaDeveloper Network`, 7 + 17 = 24 bytes. The CRLF after each chunk's data is framing, not content, so it is not counted. Reading `11` as decimal eleven would cut the chunk short and desynchronise the parser.

The key idea is that the receiver reads **exactly the number of bytes the size line announced**, then expects one CRLF. It never searches the data for line breaks, so a chunk may itself contain `\r\n` bytes without ending early.

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
