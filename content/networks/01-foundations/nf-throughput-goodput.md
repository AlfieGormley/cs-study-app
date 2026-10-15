---
id: nf-throughput-goodput
sourceLesson: nf-performance
title: Throughput and useful goodput
level: basic
minutes: 3
summary: Account for bottlenecks and overhead when translating link speed into useful payload rate.
---

## Throughput and goodput

**Throughput** is the rate at which data actually gets through, as opposed to the link's nominal rate. End to end, it is limited by the slowest link on the path, the **bottleneck**:

```formula
X ≤ min(R_1, R_2, …, R_n)
where
X: the end-to-end throughput, in bits per second
R_1, R_2, R_n: the rates of the first, second and last links on the path, in bits per second
n: the number of links on the path
…: and so on, for every link in between
min: the minimum: the smallest of the values in the brackets
≤: less than or equal to
In words: a path can never carry data faster than its slowest link.
```

A 1 Gbit/s home network behind a 100 Mbit/s broadband line gives at most 100 Mbit/s to the internet, the smaller of the two rates. Throughput is also limited by the window/RTT bound above, and by competition with other flows sharing the bottleneck.

**Goodput** is throughput counting only useful application data. It excludes:

- headers at every layer (Ethernet, IP, TCP, TLS records)
- preamble and inter-frame gap on Ethernet
- retransmitted copies of lost packets
- protocol messages that carry no data (pure ACKs, handshakes)

In a one-direction untagged full-duplex 1 Gbit/s Ethernet model with 1500-byte IPv4 packets, minimal headers and nominal preamble/gap accounting, each full frame carries 1460 TCP payload bytes in 1538 byte-times (the earlier encapsulation units):

```formula
G = (D / W)R
G = (1460 / 1538) × 1000 Mbit/s
G ≈ 949 Mbit/s
where
G: the goodput, the rate of TCP payload delivered, in megabits per second (Mbit/s)
D: the TCP data per frame, 1460 bytes
W: the wire time per frame, 1538 byte-times (the 1500-byte IP packet plus 38 bytes of Ethernet header, FCS, preamble and gap)
R: the link rate, 1000 Mbit/s (1 Gbit/s)
Mbit/s: megabits per second; 1 Mbit is 1,000,000 bits
≈: approximately equal to
In words: about 95% of the gigabit link's time carries TCP payload, so about 949 Mbit/s of it is useful data.
```

Twelve bytes of TCP options reduce that to about 941 Mbit/s. These exclude application/TLS overhead and assume hosts, ACKs and congestion do not limit the rate. If 2% of equal-sized transmissions represent extra attempts, a saturated-link accounting model loses another 2% of useful rate; actual loss can also trigger congestion control.

## Key takeaways
- The bottleneck bounds end-to-end throughput.
- Goodput excludes headers, retransmissions and control messages at the chosen accounting boundary.

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
