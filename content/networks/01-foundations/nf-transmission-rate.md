---
id: nf-transmission-rate
sourceLesson: nf-performance
title: Rate, units and transmission time
level: basic
minutes: 3
summary: Separate link capacity from latency and calculate how long a packet takes to transmit.
---

Two words get used loosely in everyday talk about networks: "fast" and "slow". A "fast" connection might mean one that moves a lot of data per second, or one that responds quickly. These are different properties, and confusing them leads to bad decisions, such as paying for more bandwidth when the real problem is latency.

This lesson gives you the vocabulary and the arithmetic. You will use it in every later lesson, especially when we reach TCP.

## Bandwidth and latency

- **Bandwidth** (or link rate, capacity) is how many bits per second a link can push onto the wire. Think of the *width* of a pipe.
- **Latency** (delay) is how long it takes one bit, or one packet, to get from one end to the other. Think of the *length* of the pipe.

A motorway analogy: bandwidth is the number of lanes, latency is how long the drive takes. Adding capacity does not shorten the physical route, but it can reduce congestion delays. Likewise, greater link rate can reduce transmission and queueing delay without changing propagation speed.

> [!warning] Units
> Network rates use decimal SI units and **bits**: 1 Mbit/s is 1,000,000 bits per second. File sizes are usually in **bytes**, sometimes binary (1 KiB = 1024 bytes). A "100 Mbit/s" connection downloads at most 12.5 MB/s. Mixing bits and bytes is the most common calculation mistake, so write the units down.

### 1. Transmission delay

The time to push all the packet's bits onto the link. Use it whenever the question is "how long does this link take to send this much data?":

```formula
d_trans = L / R
where
d_trans: the transmission delay, in seconds: the time from the first bit of the packet going onto the link to the last bit going on
L: the packet length, in bits, counted at the layer being modelled
R: the link's transmission rate (bandwidth), in bits per second
In words: double the packet and the transmission time doubles; double the link rate and it halves. The length of the cable plays no part.
```

For example, a 1500-byte packet on a 100 Mbit/s link:

```formula
L = 1500 B × 8 bit/B = 12,000 bit
R = 100 Mbit/s = 10⁸ bit/s
d_trans = 12,000 bit / (10⁸ bit/s)
d_trans = 0.00012 s = 120 µs
where
L: the packet length in bits
B: bytes; one byte is 8 bits
bit: one binary digit, the unit link rates are counted in
R: the link rate, in bits per second
Mbit/s: megabits per second; 1 Mbit is 1,000,000 bits
d_trans: the transmission delay
s: seconds
µs: microseconds; 1 µs is one millionth of a second (10⁻⁶ s)
In words: a 100 Mbit/s link needs 120 millionths of a second to put a 1500-byte packet onto the wire.
```

The table repeats this for other rates. It ignores additional framing and encoding overhead, which a real link adds on top. A 1500-byte packet is 12,000 bits:

| Link rate | d_trans |
|---|---|
| 10 Mbit/s | 1.2 ms |
| 100 Mbit/s | 120 µs |
| 1 Gbit/s | 12 µs |
| 10 Gbit/s | 1.2 µs |

## Key takeaways
- Convert bytes to bits before dividing by bit rate.
- Transmission time depends on packet length and rate, rather than route distance.

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
