---
id: app-http2-quic
title: HTTP/2 frames, HPACK and QUIC packets
level: intermediate
minutes: 17
summary: The 9-byte HTTP/2 frame header, streams and flow control, how HPACK turns headers into single bytes, then QUIC's packet formats, variable-length integers, packet numbers and connection migration.
---

The System Design lesson explained *why* HTTP/2 multiplexes and *why* HTTP/3 moved to QUIC. This lesson opens the packets. By the end you should be able to read a hex dump of an HTTP/2 frame, decode an HPACK header block by hand, and explain what a QUIC endpoint does when a phone hops from Wi-Fi to 5G.

## HTTP/2: binary frames on one connection

HTTP/2 ([RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)) keeps HTTP's semantics (methods, status codes, headers) but replaces the text format with **frames**. Frames address a **stream** or the connection (stream ID 0). HTTP request/response exchanges use streams; connection-control frames are not individual requests. Many streams interleave on one TCP connection.

### The connection preface

Over TLS, the client and server agree on HTTP/2 through ALPN (the token `h2`). The client then sends a fixed 24-byte magic string, followed by a SETTINGS frame:

```
PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n
```

The string is chosen so that an HTTP/1.1 server that receives it by mistake fails loudly rather than misinterpreting frames.

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

- **Length** is the payload size, excluding the 9-byte header. The default maximum is **16,384 bytes** (2^14); a peer can raise it with `SETTINGS_MAX_FRAME_SIZE` up to 2^24 − 1.
- **Stream ID 0** is the connection itself, used for control frames. **Client-initiated streams are odd** (1, 3, 5...), server-initiated ones even. IDs only increase and are never reused; a long-lived connection that runs out must be replaced.

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

### Flow control

HTTP/2 has its own flow control **per stream and per connection**, on top of TCP's. Before settings, each has a **65,535-byte** window. SETTINGS_INITIAL_WINDOW_SIZE adjusts stream windows; the connection window is enlarged with WINDOW_UPDATE. Sending DATA uses up window; the receiver returns credit with WINDOW_UPDATE. Only DATA payloads count, including their pad-length and padding bytes, but excluding the 9-byte frame header.

This lets a proxy stop one slow download from filling its buffers without stalling the other streams. In an ideal feedback model with prompt credit return, negligible transmission time and no other bottleneck, sustained throughput is approximately bounded by window/RTT: 65,535 bytes over 100 ms gives 5.24 Mbit/s. Delayed credit and other bottlenecks lower it. The receiver can advertise more stream credit; connection credit must also suffice.

### GOAWAY, RST_STREAM and Rapid Reset

GOAWAY reports the highest peer-initiated stream ID on which the sender might have acted or might still act. Higher-numbered requests were not processed and may be retried; lower-numbered unfinished requests may have ambiguous outcomes. That makes graceful restarts possible.

`RST_STREAM` cancels one stream cheaply. In 2023 attackers abused this in the **Rapid Reset** attack (CVE-2023-44487): open a stream with HEADERS, immediately reset it, repeat. The stream never counts against `SETTINGS_MAX_CONCURRENT_STREAMS` for long, but the server still starts work on each request. Google reported a peak of about 398 million requests per second. Mitigations can limit abusive creation/reset work or terminate offending connections; deployed protection depends on implementation and configuration.

### Priorities and push

RFC 9113 deprecated the original tree-based priority scheme. Its replacement ([RFC 9218](https://www.rfc-editor.org/rfc/rfc9218)) is a simple `priority` header, such as `u=1, i` (urgency 0 to 7, default 3; `i` means incremental). Chrome’s published removal rationale included limited performance benefit and cache-related waste; it disabled HTTP/2 server push by default starting with Chrome 106 in 2022. Other clients and non-browser use differ.

## HPACK: header compression

HTTP/1.1 headers repeat on every request: the same `user-agent`, `accept` and cookies, hundreds of bytes each time. HPACK ([RFC 7541](https://www.rfc-editor.org/rfc/rfc7541)) compresses them using three tools.

**1. A static table** of 61 common fields, numbered from 1:

| Index | Name | Value |
|---|---|---|
| 1 | :authority | |
| 2 | :method | GET |
| 3 | :method | POST |
| 4 | :path | / |
| 6 | :scheme | http |
| 7 | :scheme | https |
| 8 | :status | 200 |

**2. A dynamic table** per connection direction. Fields the encoder chooses to index are added at index **62**, pushing older entries to higher numbers. Each entry costs name length + value length + **32** bytes of overhead. When the table exceeds its limit (default 4,096 bytes), the oldest entries are evicted.

**3. Static Huffman coding** for literal strings, with a code tuned to header text. Common characters take 5 or 6 bits.

### Representations

The first bits of each field say what follows:

| Prefix | Meaning |
|---|---|
| `1xxxxxxx` | Indexed: whole field from table |
| `01xxxxxx` | Literal, add to dynamic table |
| `0000xxxx` | Literal, don't index |
| `0001xxxx` | Literal, never index |

So `:method: GET` is one byte, `1` followed by index 2 in 7 bits: `0x82`. `:scheme: https` is `0x87`.

Integers use an **N-bit prefix**. If the value fits in the prefix (less than 2^N − 1), it is stored directly. Otherwise the prefix is all ones and the remainder follows in 7-bit groups, least significant first, with the top bit meaning "more follows":

```python
def enc_int(value, n):
    if (type(value) is not int or value < 0
            or type(n) is not int
            or not 1 <= n <= 8):
        raise ValueError("bad integer")
    limit = (1 << n) - 1
    if value < limit:
        return [value]
    out = [limit]
    value -= limit
    while value >= 128:
        out.append(value % 128 + 128)
        value //= 128
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

The decoder adds `:authority: www.example.com` to the dynamic table at index 62, size 10 + 15 + 32 = 57. If the entry remains at index 62 and the encoder chooses it, a later block can send `be` (1 + 62) for the whole field. The original literal field occupied 17 bytes (representation + length + 15-byte value), not just 15.

### Why "never index" exists

The 2012 **CRIME** attack showed that compressing secrets alongside attacker-controlled data leaks the secret through compressed sizes. HPACK resists this because table entries match only whole fields, but an attacker who can inject guesses can still test whether a guessed field value is already in the table. The **never-indexed** form tells every hop, including proxies re-encoding the headers, not to put a value such as a short cookie or `authorization` token in a table.

## QUIC and HTTP/3

HTTP/2's streams are independent in the protocol but not on the wire: a gap in TCP’s ordered byte stream blocks delivery of later bytes, potentially delaying otherwise independent HTTP/2 streams. Already delivered data remains usable. QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)) moves streams, reliability and congestion control into a UDP-based protocol with TLS 1.3 built in. HTTP/3 ([RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)) maps HTTP onto it.

### Packets and frames

A UDP datagram carries one or more QUIC **packets**. Protected data packets carry **frames** (Retry and Version Negotiation have different payload formats): STREAM (data), ACK, CRYPTO (TLS handshake bytes), MAX_DATA and MAX_STREAM_DATA (flow control), NEW_CONNECTION_ID, PATH_CHALLENGE / PATH_RESPONSE, CONNECTION_CLOSE and so on.

There are two header formats:

- **Long header** (first bit 1), used during the handshake. Types: Initial, 0-RTT, Handshake and Retry. It carries the version and both connection IDs, with their lengths.
- **Short header** (first bit 0), used for 1-RTT data once the appropriate keys are available, potentially before handshake confirmation. It carries only the **Destination Connection ID** (whose length the receiver already knows) and the packet number.

```
Short header (1-RTT)
+-+-+-+-+-+-+-+-+
|0|1|S|R|R|K|P P|  first byte
+-+-+-+-+-+-+-+-+
| Dest Conn ID (0-160 bits)  |
| Packet Number (8-32 bits)  |
| Protected payload ...      |
```

The payload is encrypted. Header protection masks the packet number and selected low bits of the first byte (five for short headers, four for protected long headers). Connection IDs and other routing fields remain visible; the short-header spin bit is also outside that mask. This reduces what middleboxes can depend on, without making traffic untrackable or all headers confidential.

Initial packets are encrypted too, but with keys derived from the Destination Connection ID and a published salt, so anyone on the path can decrypt them. Initial protection does not authenticate the peer against a party able to derive those public keys; TLS authenticates the handshake. A client must expand the **UDP payload** of each datagram carrying Initial packets to at least 1,200 bytes, by padding or coalescing packets, and until the server has validated the client's address it may send at most **3×** the bytes it received. This bounds pre-validation amplification; it does not eliminate denial-of-service attacks or all reflection.

### Variable-length integers

QUIC encodes most numbers as **varints**. The top two bits of the first byte give the total length:

| Bits | Bytes | Max value |
|---|---|---|
| 00 | 1 | 63 |
| 01 | 2 | 16,383 |
| 10 | 4 | ~1.07 billion |
| 11 | 8 | ~4.6 × 10^18 |

```python
def varint(data):
    if not data:
        raise ValueError("empty varint")
    length = 1 << (data[0] >> 6)
    if len(data) < length:
        raise ValueError("truncated varint")
    v = data[0] & 0x3F
    for b in data[1:length]:
        v = (v << 8) | b
    return v, length

print(varint(bytes.fromhex("25")))
# (37, 1)
print(varint(bytes.fromhex("7bbd")))
# (15293, 2)
```

### Streams

Stream IDs are varints whose two low bits encode the type: `0x0` client-initiated bidirectional, `0x1` server-initiated bidirectional, `0x2` client unidirectional, `0x3` server unidirectional. So client request streams are 0, 4, 8... HTTP/3 uses unidirectional streams for its control stream and for **QPACK** ([RFC 9204](https://www.rfc-editor.org/rfc/rfc9204)), HPACK's successor. HPACK assumes headers arrive in order; QPACK sends table updates on dedicated streams and declares dependencies. Header blocks that reference unavailable dynamic entries can still block; encoders can avoid such references or bound the number of blocked streams.

### Packet numbers and loss recovery

TCP's sequence numbers count bytes, and a retransmission reuses them, so when an ACK arrives the sender cannot tell whether it acknowledges the original or the retransmission. TCP avoids ambiguous samples using rules such as Karn’s algorithm; timestamps can also disambiguate samples.

QUIC packet numbers increase and are never reused **within each number space**. Required lost information is carried in new packets; it need not preserve old frame boundaries, and not every frame type is retransmitted. ACK ranges identify transmissions, avoiding TCP’s retransmission ambiguity. ACK-delay correction follows RFC 9002 rules; reported delay and scheduling can still affect estimates. There are three separate **packet number spaces**: Initial, Handshake and application data. There are four encryption levels: 0-RTT and 1-RTT share the application-data number space.

## Connection migration

Ordinary TCP identifies an established connection by its endpoint addresses and ports. A changed externally visible tuple cannot simply continue that connection without additional mechanisms. A brief outage can recover if the tuple and state survive; VPNs, stable addressing or Multipath TCP can change handover behaviour. NAT rebinding can disrupt ordinary TCP, but neither every handover nor every idle period necessarily changes that tuple.

A QUIC connection is identified by **connection IDs**, not addresses. So the server can keep a connection alive when packets arrive from a new address:

```
Client (Wi-Fi 192.0.2.7)    Server
  | 1-RTT DCID=A ----------->|
  .. switches to 5G ........
Client (5G 198.51.100.4)
  | 1-RTT DCID=B ----------->| new path!
  |<---- PATH_CHALLENGE(x) --|
  | PATH_RESPONSE(x) ------->|
  |       path validated     |
```

1. **Spare connection IDs.** When nonzero connection IDs are used, endpoints can issue spare IDs with NEW_CONNECTION_ID. On a deliberate new local-address path, a fresh peer-issued ID avoids linking paths by reusing that ID. It does not prevent correlation by timing, packet sizes or an observer that sees both paths.
2. **Path validation.** The server sends PATH_CHALLENGE with 8 random bytes to the new address and needs them echoed in PATH_RESPONSE. A matching protected response validates reachability on that path. It does not establish a user’s physical location or defeat an attacker that can relay traffic. Until validation, the anti-amplification limit applies.
3. **Congestion state is reset.** The new path may have completely different bandwidth and RTT, so validation normally triggers resetting congestion and RTT state. RFC 9000 permits retaining state for a port-only address change, with caution about potentially different path characteristics.

Only the **client** may migrate actively. A server can advertise preferred_address during the handshake. disable_active_migration restricts deliberate migration to the specified server address; it does not prohibit NAT rebinding or a permitted move to the server’s preferred address.

> [!warning] Migration and load balancers
> If a layer-4 load balancer hashes the 4-tuple, a changed tuple may select a different server without connection state; collisions or shared state can produce other outcomes. A coordinated CID-aware design can maintain routing across issued IDs, using a mapping or an encoded routing hint. It must also handle Initial routing and ID lifecycle.

## HTTP/3 discovery

A client can learn HTTP/3 support from configuration, cached knowledge, DNS or an `Alt-Svc: h3=":443"` response header, and may then open a QUIC connection. The `HTTPS` DNS record ([RFC 9460](https://www.rfc-editor.org/rfc/rfc9460)) can advertise `alpn=h3` before the first connection. Clients can race or fall back to TCP when QUIC is unavailable; policy varies and UDP blocking is one possible cause.

## Key takeaways
- HTTP/2 frames have a 9-byte header: 24-bit length, type, flags and a 31-bit stream ID; odd streams are client-initiated, stream 0 is the connection.
- HTTP/2 adds per-stream and per-connection flow control (65,535-byte initial windows), and RST_STREAM abuse caused the Rapid Reset attack.
- HPACK uses a 61-entry static table, a per-connection dynamic table (entries cost size + 32) and Huffman coding; `:method: GET` is just `0x82`.
- QUIC encrypts payloads and protects selected header bits while leaving connection IDs visible. Varints use 1/2/4/8 bytes; packet numbers are unique within their number space.
- With suitable connection IDs, routing and endpoint support, QUIC can survive address changes. Path validation and fresh IDs address specific reachability and linkability risks without guaranteeing availability or anonymity.

## Further reading
- [RFC 9113: HTTP/2 — IETF](https://www.rfc-editor.org/rfc/rfc9113)
- [RFC 7541: HPACK — IETF](https://www.rfc-editor.org/rfc/rfc7541)
- [RFC 9000: QUIC — IETF](https://www.rfc-editor.org/rfc/rfc9000)
- [HTTP/2 Rapid Reset: deconstructing the record-breaking attack — Cloudflare blog](https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/)
- [HPACK: the silent killer feature of HTTP/2 — Cloudflare blog](https://blog.cloudflare.com/hpack-the-silent-killer-feature-of-http-2/)
- [The Illustrated QUIC Connection](https://quic.xargs.org/)
