---
id: net-tcp-slow-start
title: "TCP windows and slow start"
level: intermediate
minutes: 4
summary: "Explain why a new connection needs several round trips to deliver even a modest response on a fast link."
sourceLesson: net-transport-http
---
Transport performance is about how much data may be in flight, not only raw bandwidth. This unit shows why a brand-new connection is slow even on a fast link.

Every HTTP request rides on a transport protocol. The choice of transport, and how HTTP uses it, explains most of the performance differences between HTTP/1.1, HTTP/2 and HTTP/3. These short units build up from TCP and UDP to the problem each HTTP version was designed to fix.

## TCP: a reliable, ordered byte stream

TCP gives applications the illusion of a reliable pipe:

- **Connection-oriented:** a three-way handshake (SYN, SYN-ACK, ACK) costs 1 RTT before data flows.
- **Reliable:** lost segments are detected and retransmitted.
- **Ordered:** bytes are delivered to the app in the order they were sent.
- **Flow control:** the receiver advertises how much it can buffer.
- **Congestion control:** the sender probes for available bandwidth.

That last point matters for performance. A new TCP connection starts in **slow start**, with a small congestion window: commonly 10 segments, about 14 KB (proposed by the Experimental RFC 6928; the actual initial window depends on the implementation and configuration). The window roughly doubles each round trip until loss appears, after which the sender cuts it (by half for classic Reno, by about 30% for CUBIC, the Linux default) and grows more cautiously.

In an idealised model (no loss, immediate acknowledgements, a 14 KB start that doubles every round trip) the amount a fresh connection can deliver grows like this:

| Round trip | Window | Total delivered |
|---|---|---|
| 1 | 14 KB | 14 KB |
| 2 | 28 KB | 42 KB |
| 3 | 56 KB | 98 KB |
| 4 | 112 KB | 210 KB |

So a 200 KB response needs about four round trips on a new connection, whatever the link speed. That separates two costs that are easy to blur:

```formula essential
T ≈ k × RTT + 8S / B
where
T: the time to deliver a response after the request is sent, in seconds (s)
k: the number of round trips the sender needs; set by the congestion window, so 1 on a warm connection whose window already fits the response and several on a new one
RTT: the round-trip time, in seconds (s)
S: the response size, in bytes
8: the number of bits in a byte
B: the link bandwidth, in bits per second (bit/s)
≈: approximately equal to (a simplified model that ignores loss and processing)
In words: delivery time has a round-trip part and a wire part. For a small or medium response on a new connection the round-trip part dominates, so a faster link barely helps while fewer round trips help a lot.
```

For example, on a 1 Gbps link a 200 KB response needs under 2 ms of wire time, but at a 50 ms RTT the four slow-start rounds take about 200 ms. Upgrading the link would shave a millisecond; reusing a warm connection, whose window has already grown, would deliver it in about one round trip.

**Warm, reused connections are fast; new ones are slow.** This is why connection pooling and keep-alive matter so much between services as well as for browsers.

> [!note] TCP Fast Open
> TCP Fast Open (RFC 7413) lets a returning client put data in the SYN, saving the handshake RTT. Deployment depends on both endpoints and middlebox compatibility.

## Key takeaways

- TCP provides reliability, ordering, flow control and congestion control.
- A fresh connection’s small window can dominate a response even on a fast link.
- Bandwidth shortens the wire part only; reuse avoids repeated setup and window growth. The doubling model assumes no loss and simplified ACK timing.

## Further reading

- [Increasing TCP’s initial window (RFC 6928)](https://www.rfc-editor.org/rfc/rfc6928)
- [Building blocks of TCP (High Performance Browser Networking)](https://hpbn.co/building-blocks-of-tcp/)
