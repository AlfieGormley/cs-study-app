---
id: tcp-short-transfer-timing
sourceLesson: tcp-performance
title: Counting setup and response round trips
level: advanced
minutes: 3
summary: Counting setup and response round trips, with worked examples and explicit assumptions.
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

The response needs 69 segments, sent in flights of 10, 20 and 39. The request/first response costs one RTT; each further flight adds one RTT in this ideal model. Adding the round trips up:

```formula
T ≈ (N_setup + N_data) × RTT
T ≈ (2 + 3) × 100 ms = 500 ms
where
T: the time until the whole response has arrived, in milliseconds (ms)
N_setup: round trips spent on handshakes; 1 for TCP plus 1 for TLS 1.3
N_data: round trips for the request and the slow-start flights of the response; 3 here
RTT: round-trip time, 100 ms here
ms: milliseconds
≈: approximately equal to
In words: five round trips at 100 ms each make about half a second, and only the last three carry the actual data.
```

A conventional full TLS 1.2 handshake adds a round trip relative to TLS 1.3; resumptions differ. The table is an estimate under these assumptions, not a measured or universal HTTPS latency. Connection reuse and closer servers can reduce round-trip costs.

> [!note] TCP Fast Open
> TFO ([RFC 7413](https://www.rfc-editor.org/rfc/rfc7413)) can let a client with a previously obtained cookie send data in its SYN. When supported and accepted, this can save a round trip. Applications must handle replay-related restrictions and implementations need fallback for incompatible paths. This lesson makes no current browser-adoption claim.

## Key takeaways

- Setup and slow-start response flights can dominate a short transfer on a fast path.
- The five-RTT worked example makes all handshake, flight and processing assumptions explicit.
- Reuse and eligible Fast Open can reduce setup costs without guaranteeing a universal latency.

## Further reading

- [The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm — Mathis et al.](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Introduction to bufferbloat — bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Introduction/)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The QUIC Transport Protocol: Design and Internet-Scale Deployment — Google (SIGCOMM 2017)](https://research.google/pubs/the-quic-transport-protocol-design-and-internet-scale-deployment/)
- [RFC 7413: TCP Fast Open](https://www.rfc-editor.org/rfc/rfc7413)
- [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 9002: QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002)
- [Mathis and Mahdavi: Deprecating the TCP Macroscopic Model (2019 editorial)](https://ccronline.sigcomm.org/wp-content/uploads/2019/10/acmdl19-323.pdf)
