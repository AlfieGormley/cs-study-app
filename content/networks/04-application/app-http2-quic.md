---
id: app-http2-quic
title: HTTP/2 frames, HPACK and QUIC packets
level: intermediate
minutes: 17
summary: The 9-byte HTTP/2 frame header, streams and flow control, how HPACK turns headers into single bytes, then QUIC's packet formats, variable-length integers, packet numbers and connection migration.
---

The System Design lesson explained *why* HTTP/2 multiplexes and *why* HTTP/3 moved to QUIC. This lesson opens the packets. By the end you should be able to read a hex dump of an HTTP/2 frame, decode an HPACK header block by hand, and explain what a QUIC endpoint does when a phone hops from Wi-Fi to 5G.

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
L_max = 2^24 − 1 B = 16,777,215 B
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

### Flow control

HTTP/2 has its own flow control **per stream and per connection**, on top of TCP's. Before settings, each has a **65,535-byte** window. SETTINGS_INITIAL_WINDOW_SIZE adjusts stream windows; the connection window is enlarged with WINDOW_UPDATE. Sending DATA uses up window; the receiver returns credit with WINDOW_UPDATE. Only DATA payloads count, including their pad-length and padding bytes, but excluding the 9-byte frame header.

This lets a proxy stop one slow download from filling its buffers without stalling the other streams. It also caps speed: the sender can have at most one window of data in flight before the receiver returns credit, and fresh credit takes a round trip to come back. In an ideal feedback model with prompt credit return, negligible transmission time and no other bottleneck:

```formula
T_max ≈ W / RTT
T_max ≈ 65,535 B / 0.1 s = 655,350 B/s
T_max ≈ 655,350 × 8 bit/s ≈ 5.24 Mbit/s
where
T_max: the highest sustained rate the window allows, in bytes per second (B/s) or megabits per second (Mbit/s)
W: the flow-control window, in bytes (B); 65,535 B before SETTINGS changes it
RTT: the round-trip time for data to reach the receiver and its WINDOW_UPDATE credit to come back, in seconds (s); here 100 ms = 0.1 s
≈: approximately equal to; this is an upper bound under ideal assumptions
B: bytes
s: seconds
bit: one binary digit; 8 bits make a byte
Mbit: megabit, one million bits
In words: a 64 KiB window over a 100 ms round trip limits one stream to about 5 megabits per second, however fast the link is.
```

Doubling the window or halving the RTT doubles this ceiling. Delayed credit and other bottlenecks lower it. The receiver can advertise more stream credit; connection credit must also suffice.

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

**2. A dynamic table** per connection direction. Fields the encoder chooses to index are added at index **62**, pushing older entries to higher numbers. Each entry is charged a fixed overhead on top of its text, so both sides measure the table's usage the same way:

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
x: the value of the single byte that encodes an indexed field. The result is written in hexadecimal (base 16, marked by the prefix 0x): 0x82 means 8 × 16 + 2 = 130
i: the field's index in the table; 2 for :method: GET
In words: an indexed field is one byte whose top bit is set and whose other seven bits hold the index.
```

By the same rule, `:scheme: https` (index 7) is `0x87`.

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

The decoder reverses this: 31 + 26 + 10 × 128 = 1337. The same code in Python:

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

## QUIC and HTTP/3

HTTP/2's streams are independent in the protocol but not on the wire: a gap in TCP’s ordered byte stream blocks delivery of later bytes, potentially delaying otherwise independent HTTP/2 streams. Already delivered data remains usable. QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)) moves streams, reliability and congestion control into a UDP-based protocol with TLS 1.3 built in. HTTP/3 ([RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)) maps HTTP onto it.

### Packets and frames

A UDP datagram carries one or more QUIC **packets**. Protected data packets carry **QUIC frames** (Retry and Version Negotiation have different payload formats): STREAM (data), ACK, CRYPTO (TLS handshake bytes), MAX_DATA and MAX_STREAM_DATA (flow control), NEW_CONNECTION_ID, PATH_CHALLENGE / PATH_RESPONSE, CONNECTION_CLOSE and so on.

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

Initial packets are encrypted too, but with keys derived from the Destination Connection ID and a published salt, so anyone on the path can decrypt them. Initial protection does not authenticate the peer against a party able to derive those public keys; TLS authenticates the handshake. A client must expand the **UDP payload** of each datagram carrying Initial packets to at least 1,200 bytes, by padding or coalescing packets, and until the server has validated the client's address it may send at most **3×** the bytes it received:

```formula
B_sent ≤ 3 × B_recv
B_sent ≤ 3 × 1,200 B = 3,600 B
where
B_sent: the total bytes the server may send to an address it has not yet validated
B_recv: the total bytes the server has received from that address; here one minimum-size 1,200-byte Initial datagram
≤: is less than or equal to
B: bytes
In words: before the client proves it owns its address, the server may send at most three times what it received, so a spoofed 1,200-byte packet can trigger at most 3,600 bytes towards a victim.
```

This bounds pre-validation amplification; it does not eliminate denial-of-service attacks or all reflection.

### Variable-length integers

QUIC encodes most numbers as **varints**. The top two bits of the first byte give the total length:

| Bits | Bytes | Max value |
|---|---|---|
| 00 | 1 | 63 |
| 01 | 2 | 16,383 |
| 10 | 4 | ~1.07 billion |
| 11 | 8 | ~4.6 quintillion |

Each maximum comes from the bits left once the two length bits are removed:

```formula
V_max = 2^{8 × n − 2} − 1
V_1 = 2^6 − 1 = 63
V_2 = 2^14 − 1 = 16,383
V_4 = 2^30 − 1 = 1,073,741,823
V_8 = 2^62 − 1 ≈ 4.6 × 10^18
where
V_max: the largest value a varint of n bytes can hold
n: the total length of the varint in bytes: 1, 2, 4 or 8
V_1, V_2, V_4, V_8: V_max for 1, 2, 4 and 8 bytes
^: "to the power of": 2^6 means 6 copies of 2 multiplied together; 10^18 is 1 followed by 18 zeros (a quintillion)
≈: approximately equal to
In words: a varint of n bytes has 8n bits, two of which give the length, so it holds up to 2 to the power (8n − 2), minus one.
```

To decode, take the first byte, clear its top two bits (AND with `0x3F`), then append each following byte as the next 8 bits. For `7b bd`, the top bits `01` say 2 bytes:

```formula
v = (b_0 − 0x40) × 256 + b_1
v = (0x7b − 0x40) × 256 + 0xbd
v = 59 × 256 + 189 = 15,293
where
v: the decoded value
b_0: the first byte, 0x7b in hexadecimal (base 16, prefix 0x), which is 7 × 16 + 11 = 123; subtracting 0x40 (64) removes the length bits 01
b_1: the second byte, 0xbd = 11 × 16 + 13 = 189
In words: strip the two length bits from the first byte, then treat the two bytes as one big-endian number.
```

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

Stream IDs are varints whose two low bits encode the type: `0x0` client-initiated bidirectional, `0x1` server-initiated bidirectional, `0x2` client unidirectional, `0x3` server unidirectional. The rest of the bits count streams of that type:

```formula
id = 4 × k + t
id = 4 × 2 + 0 = 8
where
id: the QUIC stream ID
k: which stream of that type this is, counting from 0
t: the type in the two low bits: 0 client bidirectional, 1 server bidirectional, 2 client unidirectional, 3 server unidirectional
In words: the third client-initiated bidirectional stream (k = 2, type 0) has ID 8.
```

So client request streams are 0, 4, 8... HTTP/3 uses unidirectional streams for its control stream and for **QPACK** ([RFC 9204](https://www.rfc-editor.org/rfc/rfc9204)), HPACK's successor. HPACK assumes headers arrive in order; QPACK sends table updates on dedicated streams and declares dependencies. Header blocks that reference unavailable dynamic entries can still block; encoders can avoid such references or bound the number of blocked streams.

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
> If a layer-4 load balancer hashes the 4-tuple, a changed tuple may select a different server without connection state; hash collisions or state shared between servers can produce other outcomes. A coordinated CID-aware design can maintain routing across issued IDs, using a mapping or an encoded routing hint. It must also handle Initial routing and ID lifecycle.

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
