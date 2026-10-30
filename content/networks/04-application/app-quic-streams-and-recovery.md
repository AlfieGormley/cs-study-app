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

Stream IDs are varints whose two low bits encode the type: `0x0` client-initiated bidirectional, `0x1` server-initiated bidirectional, `0x2` client unidirectional, `0x3` server unidirectional. The remaining bits count streams of that type, so each type uses every fourth number. Either side can therefore open a new stream (within the peer's advertised stream limit) without a separate setup exchange, and the ID alone tells the receiver who opened it and whether it can reply on it.

Each stream is ordered on its own. When a packet is lost, only the streams that had data in that packet wait for the retransmission; other streams keep delivering. This is how HTTP/3 avoids the transport-level head-of-line blocking that HTTP/2 suffers over TCP. The benefit is partial: a packet carrying QUIC frames from several streams blocks all of them, so senders avoid mixing more streams into a packet than they need. All streams also still share one connection's congestion control and flow-control limits.

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
