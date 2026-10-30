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

- **Length** is the payload size, excluding the 9-byte header. The default maximum is **16,384 bytes** (16 KiB); a peer can raise it with `SETTINGS_MAX_FRAME_SIZE` up to the largest number a 24-bit field can hold, 16,777,215 bytes (just under 16 MiB).
- **Stream ID 0** is the connection itself, used for connection-control HTTP/2 frames. **Client-initiated streams are odd** (1, 3, 5...), server-initiated ones even. IDs only increase and are never reused. The 31-bit field tops out at about 2.1 billion, so one connection can open about 1.07 billion client streams; a long-lived connection that runs out must be replaced.

> [!analogy] Real-world analogy: Labelled parcels sharing one van
> A courier packs parcels for many customers into one van. Every parcel carries the same small label: how big it is, what kind of item it is, and which customer it belongs to. Notes for the depot itself are addressed to customer 0.
>
> **How it maps:** The van is the single TCP connection, each parcel is a frame, and the label is the fixed 9-byte header: length, type, flags and stream ID. A customer's parcels are one stream, and customer 0 is the connection-control traffic on stream 0. Because every label has the same layout, the receiver can always find where one frame ends and the next begins.
>
> **Where it stops:** A real courier who loses one parcel can still hand over the others. TCP cannot: it delivers bytes strictly in order, so one lost segment holds back every later HTTP/2 frame, whatever its stream, until it is resent. The QUIC units return to this limit.

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
