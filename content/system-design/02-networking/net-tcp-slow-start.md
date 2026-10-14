---
id: net-tcp-slow-start
title: "TCP windows and slow start"
level: intermediate
minutes: 4
summary: "Calculate the round-based cost of a growing TCP window and distinguish it from wire speed."
sourceLesson: net-transport-http
---
Transport performance is about how much data may be in flight as well as raw bandwidth. Use the following explicit slow-start assumptions to trace a small response round by round.

Every HTTP request rides on a transport protocol. The choice of transport, and how HTTP uses it, explains most of the performance differences between HTTP/1.1, HTTP/2 and HTTP/3. These short units build up from TCP and UDP to the problem each HTTP version was designed to fix.

## TCP: a reliable, ordered byte stream

TCP gives applications the illusion of a reliable pipe:

- **Connection-oriented:** a three-way handshake (SYN, SYN-ACK, ACK) costs 1 RTT before data flows.
- **Reliable:** lost segments are detected and retransmitted.
- **Ordered:** bytes are delivered to the app in the order they were sent.
- **Flow control:** the receiver advertises how much it can buffer.
- **Congestion control:** the sender probes for available bandwidth.

That last point matters for performance. A new TCP connection starts in **slow start**, with a small congestion window (typically 10 segments ≈ 14 KB, proposed by the Experimental RFC 6928; the actual initial window is implementation/configuration dependent). It roughly doubles each RTT until loss appears, after which the sender cuts its window (by half for classic Reno, by about 30% for CUBIC, the Linux default) and grows more cautiously. So a fresh connection can't use a fast link fully for several round trips. In the idealised model below, the window starts at 10 full segments and doubles every round trip:

```formula
IW = 10 × MSS
IW = 10 × 1,460 B = 14,600 B ≈ 14 KB
W_k = IW × 2^{k − 1}
S_k = IW × (2^k − 1)
S_4 = 14 KB × (2^4 − 1) = 210 KB
where
IW: the initial congestion window: how much data a new connection may send in its first round trip, in bytes (B)
MSS: the maximum segment size: the most data one TCP segment carries, typically 1,460 B on an Ethernet path
B: bytes
KB: kilobytes; 1 KB is 1,000 bytes here, and 14,600 B is rounded down to 14 KB
≈: approximately equal to
W_k: the congestion window during round trip number k, in KB
k: which round trip we are on: 1 for the first, 2 for the second, and so on
S_k: the total data sent after k round trips, in KB
S_4: the total after 4 round trips, as in the last row of the table below
In words: the window doubles every round trip, so after k rounds the total sent is the first window times one less than 2 to the power k.
```

| RTT # | Window | Cumulative sent |
|---|---|---|
| 1 | 14 KB | 14 KB |
| 2 | 28 KB | 42 KB |
| 3 | 56 KB | 98 KB |
| 4 | 112 KB | 210 KB |

In this idealised round-based model, a 200 KB response needs four transmission rounds, assuming a 14 KB starting window, doubling each round, no loss, immediate ACKs and negligible serialisation (the time to clock the bits onto the wire). This is not an exact packet-timing model or a bandwidth-independent guarantee. Compare how long the link itself needs with how long slow start takes:

```formula
t_wire = 8 × size / rate
t_wire = 8 × 200,000 B / 10^9 bit/s
t_wire = 0.0016 s = 1.6 ms
t_slow = rounds × RTT
t_slow = 4 × 50 ms = 200 ms
where
t_wire: the serialisation time: how long the link takes to clock the response out, in seconds (s) or milliseconds (ms)
size: the response size in bytes (B); 200 KB = 200,000 B
8: the number of bits in a byte
rate: the link speed in bits per second (bit/s); 1 Gbps (gigabit per second) = 10^9 bit/s
B: bytes
bit/s: bits per second
t_slow: the transfer time when slow start is the limit, in ms
rounds: the round trips slow start needs to deliver the response; 4 for 200 KB, from the table
RTT: the round-trip time, here 50 ms
s: second
ms: millisecond, one thousandth of a second
In words: the wire could deliver 200 KB in under 2 ms, but a new connection's growing window stretches it over four round trips, about 200 ms.
```

**Warm, reused connections are fast; new ones are slow.**

> [!note] TCP Fast Open
> TCP Fast Open (RFC 7413) lets a returning client put data in the SYN, saving the handshake RTT. Deployment depends on both endpoints and middlebox compatibility.

## Key takeaways

- TCP provides reliability, ordering, flow control and congestion control.
- A fresh connection’s small window can dominate a response even on a fast link.
- The doubling model assumes no loss and simplified ACK timing; reuse avoids repeated setup and growth.

## Further reading

- [Increasing TCP’s initial window (RFC 6928)](https://www.rfc-editor.org/rfc/rfc6928)
- [Building blocks of TCP (High Performance Browser Networking)](https://hpbn.co/building-blocks-of-tcp/)
