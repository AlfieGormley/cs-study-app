---
id: nf-complete-hop-delay
sourceLesson: nf-performance
title: Combine the four delays
level: basic
minutes: 3
summary: Diagnose four delay components and explain store-and-forward packet pipelining.
---

A packet can be delayed before transmission, during transmission, while travelling, and while a device examines it. Separating these costs helps identify which change could improve a slow path.

## Four contributions

- **Queueing:** waiting behind traffic that shares the output link. An idle link can have no queueing delay; a congested one can add hundreds of milliseconds.
- **Transmission:** putting every packet bit onto the link. Packet size and link rate determine this.
- **Propagation:** the signal travelling along the route. Distance and medium determine this.
- **Processing:** examining headers, checking errors and deciding what to do. Hardware, software, enabled features and load affect the time.

Variation in packet delay is commonly called **jitter**. Queueing contributes to jitter, but is not its only possible source.

To model one hop, add the relevant waiting, transmission, propagation and processing times. For a whole path, account for each link and each device once at the chosen timing boundary.

## Store-and-forward and pipelining

With **store-and-forward**, a device receives the complete packet before sending it onward. One packet crossing two such links therefore pays a transmission delay on each link. **Cut-through** forwarding can overlap reception with onward transmission and needs a different model.

For a concrete two-link example, assume a 1500-byte packet, two 100 Mbit/s links spanning 200 km and 800 km, one router taking 20 microseconds, no queues and no framing overhead. At the assumed 5 microseconds per kilometre, propagation contributes 5 ms; both transmissions and processing together contribute 0.26 ms. The total is about 5.26 ms. Increasing link rate addresses only part of this example's delay.

Splitting a message into packets lets different links work on different packets simultaneously. On equal-rate, initially idle links, later packets can follow the first one at one packet-transmission interval apart. For this illustration, ignore propagation and processing; each row is one packet-transmission interval:

| Interval | Link 1 | Link 2 | Link 3 |
|---|---|---|---|
| First | P1 | — | — |
| Second | P2 | P1 | — |
| Third | P3 | P2 | P1 |
| Fourth | — | P3 | P2 |
| Fifth | — | — | P3 |

Each router still receives a whole packet before forwarding it; work overlaps across links. Two packets do not transmit simultaneously on the same serial link. Extra per-packet headers are excluded from this illustration: splitting too finely can waste capacity.

## Key takeaways
- Different delay components respond to different improvements.
- Store-and-forward repeats transmission per link; packet pipelining overlaps work across links.

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
