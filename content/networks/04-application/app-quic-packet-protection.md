---
id: app-quic-packet-protection
title: "QUIC packets, protection and amplification limits"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "QUIC adds reliable streams above UDP and protects payloads plus selected header bits."
---

## QUIC and HTTP/3

HTTP/2's streams are independent in the protocol but not on the wire. TCP delivers one ordered byte stream, so when a segment carrying part of one response is lost, every later byte waits for the retransmission, including bytes of other responses that arrived safely. On a lossy mobile link one loss can briefly stall every request on the connection. This is transport-level **head-of-line blocking**; already delivered data remains usable. QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)) moves streams, reliability and congestion control into a UDP-based protocol with TLS 1.3 built in. HTTP/3 ([RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)) maps HTTP onto it.

### Packets and QUIC frames

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

In this wire diagram, S is the optional spin bit, R marks reserved bits, K is the key-phase bit and the two P bits encode a packet-number length of one, two, three or four bytes. The first zero selects the short-header form and the following fixed bit is one in QUIC version 1. The receiver already knows the connection-ID length from connection state.

The payload is encrypted. Header protection masks the packet number and selected low bits of the first byte (five for short headers, four for protected long headers). Connection IDs and other routing fields remain visible; the short-header spin bit is also outside that mask. This reduces what middleboxes can depend on, without making traffic untrackable or all headers confidential.

Initial packets are encrypted too, but with keys derived from the Destination Connection ID and a published salt, so anyone on the path can decrypt them. Initial protection does not authenticate the peer against a party able to derive those public keys; TLS authenticates the handshake.

UDP has no handshake, so a server cannot tell whether a new client's source address is genuine. An attacker could spoof a victim's address and make the server send its large handshake reply to the victim. QUIC limits this in two ways:

- A client must expand the **UDP payload** of each datagram carrying Initial packets to at least 1,200 bytes, by padding or coalescing packets.
- Until the server has validated the client's address, it may send at most **three times** the bytes it has received from that address. One 1,200-byte Initial therefore allows at most 3,600 bytes in reply.

A large certificate chain can hit that limit. The server then waits for more bytes from the client (its acknowledgements and probes also count) or for address validation, which can cost an extra round trip; RFC 9000 requires clients to keep sending on a probe timeout so the two sides cannot deadlock. The limit bounds pre-validation amplification; it does not eliminate denial-of-service attacks or all reflection.

## Key takeaways
- QUIC adds reliable streams above UDP and protects payloads plus selected header bits.
- Publicly derived Initial keys do not authenticate a peer; address validation bounds server amplification.

## Further reading
- [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)
- [RFC 9001](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 9114](https://www.rfc-editor.org/rfc/rfc9114)
