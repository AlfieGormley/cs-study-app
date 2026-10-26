---
id: nf-throughput-goodput
sourceLesson: nf-performance
title: Throughput and useful goodput
level: basic
minutes: 3
summary: Separate bottleneck capacity, achieved throughput and useful payload goodput.
---

A link's nominal capacity, the traffic it actually carries, and the useful data delivered to an application are different measurements.

## The bottleneck sets a ceiling

**Throughput** is the rate actually achieved at a stated boundary. A path cannot carry traffic faster than its slowest link, the **bottleneck**. A 1 Gbit/s home LAN behind a 100 Mbit/s broadband link can reach the internet at no more than 100 Mbit/s through that route.

Competition with other flows, active window limits, host performance and congestion can make the achieved rate lower still. A bottleneck capacity is a ceiling, not a promised result.

## Goodput counts useful data once

**Goodput** counts useful application data delivered per second. It excludes headers, duplicate transmission attempts, pure acknowledgements and handshakes. State the boundary: TCP payload rate can still include TLS or application-protocol overhead that file goodput excludes.

For the earlier one-direction, untagged full-duplex Ethernet model, a 1500-byte IPv4 packet with minimal TCP/IP headers carries 1460 bytes of TCP payload in 1538 byte-times of wire occupancy. On 1 Gbit/s Ethernet that allows about 949 Mbit/s of TCP payload. Twelve bytes of TCP options lower it to about 941 Mbit/s.

These are ideal framing ceilings. They assume hosts, acknowledgement handling, congestion and loss do not constrain the rate, and exclude additional application/TLS overhead.

## What retransmissions change

A retransmission may finally deliver data that was lost, but delivering that payload then consumed more than one attempt. Goodput counts the useful payload once.

In a saturated-link accounting model with equal payload sizes and 2% of attempts being extra retransmissions, useful rate falls by another 2% after framing overhead. Real loss can additionally trigger congestion control, idle time or timeouts, so this accounting is not a general loss-to-throughput prediction.

When a transfer is slow, measure the bottleneck, retries, window limits and host work. A higher line-rate label alone does not explain the outcome.

## Key takeaways
- Bottleneck capacity bounds throughput; other constraints can reduce it further.
- Goodput excludes overhead and counts useful delivered bytes only once.
- Retransmission accounting alone does not predict TCP's congestion response.

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
