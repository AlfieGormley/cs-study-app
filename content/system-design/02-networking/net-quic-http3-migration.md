---
id: net-quic-http3-migration
title: "QUIC streams, discovery and migration"
level: intermediate
minutes: 3
summary: "Explain HTTP/3’s loss isolation and the deployment conditions for discovery, fallback and migration."
sourceLesson: net-transport-http
---
HTTP/3 runs HTTP over QUIC rather than one ordered TCP byte stream. The diagrams below isolate application-stream delivery from the connection-wide effects of congestion control.

## HTTP/3 and QUIC: fixing transport HOL blocking

HTTP/3 (RFC 9114, 2022) runs over **QUIC** (RFC 9000, 2021), a transport built on UDP. QUIC re-implements reliability and congestion control, and it tracks **ordering per stream**:

- A loss of application stream data does not create TCP-style ordering dependencies between otherwise independent streams.
- Other streams keep flowing.

```
QUIC packets: [A1][B1][xx][A2][C2]
                  lost ^ (B2)
A1, A2, C2 delivered at once.
Only stream B waits for B2.
```

Two subtleties. Ordering still holds *within* a stream, so a loss does stall that one stream. And congestion control is still per connection, so loss slows the whole connection's sending rate even though it no longer blocks delivery. HTTP/3 also replaced HPACK with **QPACK**, because HPACK assumes headers arrive in order, which would have reintroduced cross-stream blocking. QPACK bounds and manages header dependencies; it does not eliminate every possible cross-stream dependency.

QUIC brings several other wins:

1. **Combined handshake.** Transport and TLS 1.3 are negotiated together in the same packets: 1 RTT for a new connection instead of TCP's 1 plus TLS's 1, and **0-RTT** for resumption, where the request rides in the very first flight (with replay caveats; see the TLS lesson).
2. **Connection migration.** Nonzero *connection IDs* let endpoints identify connections across changes to the IP/port 4-tuple. A phone can keep its connection when changing networks if migration is supported and permitted; path validation and connection-ID handling still matter.
3. **Encrypted application traffic.** QUIC encrypts application data and protects parts of its transport headers, reducing middlebox dependence on protocol details. Some routing fields stay visible. The first setup packets use publicly derivable keys, so their TLS ClientHello is observable unless ECH protects it.
4. **User-space implementation.** It can evolve with app releases, not OS kernel upgrades.

Costs and caveats:

- **CPU:** UDP processing in user space has historically cost more CPU than kernel TCP (improving with offloads like GSO).
- **Blocked UDP:** some corporate networks block UDP 443. Browsers fall back to HTTP/2 over TCP.
- **Discovery:** browsers usually learn about HTTP/3 from an `Alt-Svc` header on an HTTP/2 response, or from a DNS `HTTPS` record, so the first visit is often HTTP/2.
- **Load balancing:** migration needs packets to keep reaching the endpoint with connection state. A balancer that hashes only the changing 4-tuple can send them to another backend; connection-ID-aware routing or equivalent forwarding support avoids that failure.

## Side by side

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | QUIC/UDP |
| Concurrency | ~6 conns | Streams, 1 conn | Streams, 1 conn |
| HTTP HOL | Yes | No | No |
| TCP HOL | Per conn | Yes, all streams | No |
| New conn setup | 2 RTT | 2 RTT | 1 RTT |
| Resumed, 0-RTT | 1 RTT | 1 RTT | 0 RTT |

Setup figures assume TLS 1.3 and count round trips before the request can be sent. A full TLS 1.2 handshake adds one more RTT over TCP. With TLS 1.3 0-RTT over TCP, the TCP handshake still has to happen first, which is why it's 1 RTT rather than 0.

## Key takeaways

- QUIC tracks application ordering per stream, but congestion control is still shared across the connection.
- A combined transport/TLS handshake saves a setup round trip; early data carries replay caveats.
- Migration needs connection-ID-aware routing, discovery may delay first-visit HTTP/3, and blocked UDP needs TCP fallback.

## Further reading

- [QUIC (RFC 9000)](https://www.rfc-editor.org/rfc/rfc9000)
- [HTTP/3 (RFC 9114)](https://www.rfc-editor.org/rfc/rfc9114)
- [Service binding and HTTPS records (RFC 9460)](https://www.rfc-editor.org/rfc/rfc9460)
