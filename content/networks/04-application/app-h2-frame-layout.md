---
id: app-h2-frame-layout
title: "HTTP/2 frame headers and pseudo-headers"
level: intermediate
minutes: 4
sourceLesson: app-http2-quic
summary: "HTTP/2 interleaves streams over one TCP connection using fixed nine-byte frame headers."
---

HTTP/2 keeps HTTP methods, statuses and headers but changes their wire representation. Reading a frame requires separating its fixed header from its length-delimited payload.

## HTTP/2: binary frames on one connection

HTTP/2 ([RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)) keeps HTTP's semantics (methods, status codes, headers) but replaces the text format with binary **HTTP/2 frames**. Each HTTP/2 frame addresses an **HTTP/2 stream** or the connection (stream ID 0). HTTP request/response exchanges use streams; connection-control HTTP/2 frames are not individual requests. Many streams interleave on one TCP connection.

### The connection preface

Over TLS, the client and server agree on HTTP/2 through ALPN (the token `h2`). The client then sends a fixed 24-byte magic string, followed by a SETTINGS frame:

```
PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n
```

The string is chosen so that an HTTP/1.1 server that receives it by mistake fails loudly rather than misinterpreting HTTP/2 frames.

### The frame header

Every frame starts with exactly **9 bytes**:

```
+-----------------------------+
| Length (24 bits)            |
+--------------+--------------+
| Type (8)     | Flags (8)    |
+-+------------+--------------+
|R| Stream Identifier (31)    |
+-+---------------------------+
| Payload (Length bytes) ...  |
+-----------------------------+
```

- **Length** is the payload size, excluding the 9-byte header. The default maximum is **16,384 bytes**; a peer can raise it with `SETTINGS_MAX_FRAME_SIZE` up to the largest number a 24-bit field can hold.
- **Stream ID 0** is the connection itself, used for connection-control HTTP/2 frames. **Client-initiated streams are odd** (1, 3, 5...), server-initiated ones even. IDs only increase and are never reused; a long-lived connection that runs out must be replaced.

Both limits are powers of two, because a field with a given number of bits holds every whole number from 0 up to two to the power of that number, minus one:

```formula
L_default = 2^14 B = 16,384 B
L_max = (2^24 − 1) B = 16,777,215 B
N_streams = 2^31 − 1 = 2,147,483,647
where
L_default: the default maximum frame payload, in bytes (B), before any SETTINGS change
L_max: the largest payload length the 24-bit Length field can express, which is also the highest value SETTINGS_MAX_FRAME_SIZE may set
N_streams: the largest stream identifier the 31-bit field can hold
^: "to the power of": 2^14 means 14 copies of 2 multiplied together
B: bytes
In words: the default frame payload limit is 16 KiB, a peer may raise it to just under 16 MiB, and stream IDs run out after about 2.1 billion.
```

Because client streams use only the odd numbers, one connection can open at most about 1.07 billion client streams before it must be replaced.

The frame types:

| Type | Name | Purpose |
|---|---|---|
| 0x0 | DATA | Body bytes |
| 0x1 | HEADERS | Header block |
| 0x3 | RST_STREAM | Cancel one stream |
| 0x4 | SETTINGS | Connection parameters |
| 0x5 | PUSH_PROMISE | Server push |
| 0x6 | PING | Liveness, RTT |
| 0x7 | GOAWAY | Graceful shutdown |
| 0x8 | WINDOW_UPDATE | Flow control |
| 0x9 | CONTINUATION | More header block |

(0x2, PRIORITY, is deprecated.) Important flags are `END_STREAM` (0x1, this side is done), `END_HEADERS` (0x4) and `ACK` (0x1 on SETTINGS and PING).

A bodyless GET whose field block fits in one frame can use HEADERS with END_HEADERS and END_STREAM (0x05). Larger field blocks use CONTINUATION frames. A response may end on HEADERS, DATA or trailing HEADERS; informational responses and trailers add further possibilities.

```
00 00 0d   length 13
01         type HEADERS
05         END_STREAM|END_HEADERS
00 00 00 01 stream 1
<13 bytes of HPACK>
```

### Pseudo-headers

The request line becomes **pseudo-header fields**, which start with a colon and must come first: `:method`, `:scheme`, `:authority` (replacing `Host`) and `:path`. Responses have `:status`. All header names must be **lowercase**, and connection-specific headers (`Connection`, `Keep-Alive`, `Transfer-Encoding`) are forbidden.

## Key takeaways
- HTTP/2 interleaves streams over one TCP connection using fixed nine-byte frame headers.
- Stream IDs and pseudo-headers identify exchanges; lowercase names and field rules still apply.

## Further reading
- [RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)
