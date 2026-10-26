---
id: nf-flight-window
sourceLesson: nf-performance
title: Data in flight and window limits
level: basic
minutes: 3
summary: Explain why long, high-capacity paths need more data in flight and can be window-limited.
---

A sender learns that data arrived only when an acknowledgement (**ACK**) returns. A high-capacity path with a long round trip can therefore hold a lot of sent-but-unacknowledged data.

## Keeping enough data in flight

To sustain a target payload rate, a steady sender needs permission to keep roughly a round trip's worth of payload in flight. This is the **bandwidth-delay product**. A higher target rate or longer acknowledgement round-trip time increases the required flight allowance.

```formula reference
BDP = R RTT
where
BDP: bandwidth-delay product, the target amount of unacknowledged payload in bits
R: target payload rate in bits per second
RTT: acknowledgement round-trip time in seconds, from sending data until its acknowledgement returns
In words: sustaining a higher payload rate or waiting longer for feedback requires more data in flight; doubling either doubles the steady flight-size target.
```

At a hypothetical 1 Gbit/s payload rate and 70 ms acknowledgement RTT, about 8.75 MB would be unacknowledged. This is a payload target, not a universal socket-memory setting: actual operating-system buffer accounting differs.

## A window can be the bottleneck

The **TCP send window** limits how much data may remain unacknowledged. If it is too small for the target rate and RTT, the sender must wait even when the path has spare capacity.

ACKs can advance a sliding window continuously; the sender need not stop after each batch. Nevertheless, in a steady window-limited model, its delivered rate is bounded by about one window's worth per round trip.

```formula reference
X ≤ W / RTT
where
X: steady payload throughput in bits per second
W: the active allowance for unacknowledged payload in bits
RTT: acknowledgement round-trip time in seconds
≤: less than or equal to; this is an upper bound rather than a throughput prediction
In words: a fixed flight allowance supports less throughput when acknowledgements take longer to return, even if link capacity is plentiful.
```

Without negotiated **window scaling**, TCP's 16-bit receive-window field represents at most 65,535 bytes. If this is the active limit over a 70 ms RTT, it caps steady payload throughput near 7.5 Mbit/s. Window scaling allows larger advertised receive windows when negotiated; sender congestion limits, receiver space and other constraints still apply.

Paths with large bandwidth-delay products are called **long fat networks**. They need adequate flight allowances, appropriate buffering and recovery that handles many packets in flight. Simply increasing a physical link's rate may leave the limiting window unchanged.

## Key takeaways
- Higher target rates and longer feedback delays need more payload in flight.
- A small active window can limit throughput despite spare link capacity.
- Window scaling increases representable receive windows; it does not remove all throughput limits.

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
