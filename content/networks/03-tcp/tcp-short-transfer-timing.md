---
id: tcp-short-transfer-timing
sourceLesson: tcp-performance
title: Counting setup and response round trips
level: advanced
minutes: 3
summary: Why small transfers are limited by round trips rather than bandwidth, and what saves those round trips.
---

The previous lessons explained how TCP works. This one asks why a transfer is slower than the link, and what engineers at CDNs, browser vendors and cloud providers do about it.

There are three usual suspects:

1. **Round trips**: handshakes and slow start, which bound short transfers.
2. **Loss**: which bounds long transfers through congestion control.
3. **Queues**: which add delay that nobody asked for.

Deployment is another constraint: transport changes must work with deployed endpoints and middleboxes. QUIC provides an alternative design over UDP.

## Short transfers are latency-bound

For small responses on a sufficiently fast link, handshake and request round trips can dominate. Serialization, server work, DNS, certificate size and loss can also matter.

Illustrative model: fetch 100,000 payload bytes over a new TCP + TLS 1.3 connection at 100 ms RTT, with MSS 1,460 bytes, initial window 10 segments, ideal doubling per completed flight, negligible serialization/server processing, no DNS delay, no loss, no TLS retry and no other limits. Ignore handshake bytes when modelling the response window:

| Step | Round trips |
|---|---|
| TCP handshake | 1 |
| TLS 1.3 handshake | 1 |
| Request, then slow start: 10, 20, 39 segments | 3 |
| Total | about 5 (500 ms) |

The response needs 69 segments, sent in flights of 10, 20 and 39. The request/first response costs one RTT; each further flight adds one RTT in this ideal model. Five round trips at 100 ms is about half a second, and only the last three carry the actual data. Note what does not appear: the link's bandwidth. On a fast link, a faster link would barely change this total; fewer round trips or shorter ones would.

A conventional full TLS 1.2 handshake adds a round trip relative to TLS 1.3; resumptions differ. The table is an estimate under these assumptions, not a measured or universal HTTPS latency. Connection reuse and closer servers can reduce round-trip costs.

> [!note] TCP Fast Open
> TFO ([RFC 7413](https://www.rfc-editor.org/rfc/rfc7413)) can let a client with a previously obtained cookie send data in its SYN. When supported and accepted, this can save a round trip. Applications must handle replay-related restrictions and implementations need fallback for incompatible paths. This lesson makes no current browser-adoption claim.

## Key takeaways

- Setup and slow-start response flights can dominate a short transfer on a fast path.
- The five-RTT worked example makes all handshake, flight and processing assumptions explicit.
- Reuse and eligible Fast Open can reduce setup costs without guaranteeing a universal latency.

## Further reading

- [RFC 7413: TCP Fast Open](https://www.rfc-editor.org/rfc/rfc7413)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
