---
id: nf-flight-window
sourceLesson: nf-performance
title: Data in flight and window limits
level: basic
minutes: 4
summary: Calculate bandwidth-delay product and understand a receive-window throughput bound.
---

## The bandwidth-delay product

For a steady window-limited flow, how much unacknowledged data corresponds to a target payload rate? A sender learns that data arrived only when an acknowledgement (ACK) comes back, one round trip after sending it. To keep sending throughout that round trip, it needs a full round trip's worth of data in flight. Multiply the rate by the acknowledgement round-trip time, using consistent units:

```formula
BDP = R RTT
where
BDP: the bandwidth-delay product, in bits: the amount of data sent but not yet acknowledged when the path is kept full
R: the target payload rate, in bits per second
RTT: the round-trip time: from sending data until its acknowledgement arrives, in seconds
In words: a fast or long path holds a lot of data "in the pipe" at once; double either the rate or the RTT and the data in flight doubles.
```

For a hypothetical payload rate of 1 Gbit/s and a 70 ms RTT:

```formula
BDP = 10⁹ bit/s × 0.070 s
BDP = 7 × 10⁷ bit = 70 Mbit
BDP = 70 Mbit / 8 = 8.75 MB
where
BDP: the bandwidth-delay product
bit: one binary digit; bit/s is bits per second
s: seconds; 70 ms is 0.070 s
Mbit: megabits; 1 Mbit is 1,000,000 bits
MB: megabytes; 1 MB is 1,000,000 bytes, and there are 8 bits in a byte
In words: to keep a 1 Gbit/s, 70 ms path full, about 8.75 MB must be sent and still awaiting acknowledgement at any moment.
```

That is how much a sender must have sent but not yet had acknowledged to keep the pipe full. If the sender's **TCP send window** (the amount it may have unacknowledged) is smaller than the BDP, it sits idle waiting for acknowledgements. It can send at most one window per round trip, so throughput is capped at:

```formula
X ≤ W / RTT
where
X: the throughput, in bits per second
W: the window: the most data the sender may have sent but not yet had acknowledged, in bits
RTT: the round-trip time, in seconds
≤: less than or equal to (this is an upper limit, not a prediction)
In words: one window per round trip is the most a window-limited sender can manage, however fast the link is.
```

> [!example] The original TCP window limit
> Without negotiated window scaling, TCP’s 16-bit advertised receive window cannot represent more than 65,535 bytes. This bounds steady new-data throughput when that window is the active constraint. Over a 70 ms RTT the calculation below caps throughput at about **7.5 Mbit/s**, no matter how fast the link is. The TCP **window scale** option (RFC 7323) allows larger receive windows when both endpoints negotiate it; support and configuration must be checked.

```formula
X ≤ (65,535 B × 8 bit/B) / 0.070 s
X ≤ 524,280 bit / 0.070 s
X ≤ 7.5 × 10⁶ bit/s = 7.5 Mbit/s
where
X: the throughput limit
B: bytes; one byte is 8 bits, so bit/B is bits per byte
bit: one binary digit
s: seconds; 70 ms is 0.070 s
Mbit/s: megabits per second (millions of bits per second)
In words: a 65,535-byte window delivered once every 70 ms is about 7.5 Mbit/s, under 1% of a gigabit link.
```

Paths with a large BDP are called **long fat networks**. They need large windows, large socket buffers and loss recovery that copes with many packets in flight. The error-control units and the TCP module build on this.

## Key takeaways
- The target payload rate times acknowledgement RTT gives a steady flight-size target.
- An active window limit can constrain throughput even on a high-capacity path.

## Further reading
- [Primer on Latency and Bandwidth — High Performance Browser Networking](https://hpbn.co/primer-on-latency-and-bandwidth/)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)
- [Network delay — Wikipedia](https://en.wikipedia.org/wiki/Network_delay)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Bufferbloat — Wikipedia](https://en.wikipedia.org/wiki/Bufferbloat)
- [Goodput — Wikipedia](https://en.wikipedia.org/wiki/Goodput)

- [RFC 8290: FQ-CoDel](https://www.rfc-editor.org/rfc/rfc8290)
- [RFC 8446: TLS 1.3 and early-data replay considerations](https://www.rfc-editor.org/rfc/rfc8446)
- [MIT queueing lecture: M/M/1 assumptions](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-spring-2006/1a538356bf7a1f78408de525dd2d1032_lec21.pdf)
