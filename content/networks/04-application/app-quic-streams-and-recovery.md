---
id: app-quic-streams-and-recovery
title: "QUIC stream IDs, QPACK and loss recovery"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "QUIC stream IDs encode initiator and direction in their two low bits."
---

QUIC carries several independently ordered byte streams over a connection. HTTP/3 maps requests to client-initiated bidirectional streams and uses dedicated streams for control and QPACK compression state.

### Streams

Stream IDs are varints whose two low bits encode the type: `0x0` client-initiated bidirectional, `0x1` server-initiated bidirectional, `0x2` client unidirectional, `0x3` server unidirectional. The rest of the bits count streams of that type:

```formula
id = 4k + t
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

## Key takeaways
- QUIC stream IDs encode initiator and direction in their two low bits.
- Packet numbers identify transmissions within three number spaces; lost data can move to new packets.

## Further reading
- [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)
- [RFC 9002](https://www.rfc-editor.org/rfc/rfc9002)
- [RFC 9204](https://www.rfc-editor.org/rfc/rfc9204)
