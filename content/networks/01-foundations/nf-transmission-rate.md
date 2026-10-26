---
id: nf-transmission-rate
sourceLesson: nf-performance
title: Rate, units and transmission time
level: basic
minutes: 3
summary: Distinguish link capacity from latency and predict how packet size and link rate affect transmission.
---

A connection can move a lot of data each second yet respond slowly. Buying more bandwidth helps when capacity is the constraint; it cannot make a signal travel a fixed route faster.

## Bandwidth and latency

**Bandwidth**, also called link rate or capacity here, is how many bits a link can put onto the medium per second. **Latency** is the time a bit or packet takes to reach its destination, using the timing boundary specified.

> [!analogy] Real-world analogy: More lanes
> Adding lanes to a road lets more vehicles travel at once. It does not shorten the route.
>
> **How it maps:** Link capacity is like the number of lanes; propagation time is like the journey along the route. More capacity can reduce congestion and the time needed to send a whole packet.
>
> **Where it stops:** Packets are serialised into signals, and routers add processing and queueing. A road journey does not model all those delays.

> [!warning] Bits and bytes
> Network rates use decimal SI units and bits: 1 Mbit/s is 1,000,000 bits per second. One byte is 8 bits. File sizes may use decimal bytes (MB) or binary units (KiB, with 1024 bytes per KiB). A 100 Mbit/s link has an ideal ceiling of 12.5 MB/s before overhead; a browser's displayed rate requires measurement.

## Transmission delay

Transmission delay is the time to put all of one packet's bits onto the link, from its first bit to its last. Larger packets take longer. A higher link rate sends the same packet in less time. Cable length plays no part in this particular delay.

```formula reference
d_trans = L / R
where
d_trans: transmission delay, in seconds, from putting the first packet bit onto the link to putting the last bit onto it
L: packet length in bits, counted at the layer being modelled
R: link rate in bits per second
In words: transmission takes longer for a larger packet and less time on a higher-rate link; doubling both packet size and link rate leaves this delay unchanged.
```

For example, putting a 1500-byte packet onto a 100 Mbit/s link takes 120 microseconds, ignoring additional framing and encoding. At 1 Gbit/s it takes 12 microseconds. The signal still needs time to travel after the first bit enters the medium.

Overhead, server work, congestion and host limits can make a file transfer slower than the raw rate suggests. Keep the units and the measured boundary explicit.

## Key takeaways
- Capacity describes a rate; latency describes a time.
- Packet size and link rate determine transmission delay; route length determines a different delay.

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
