---
id: tcp-slow-start-flights
sourceLesson: tcp-congestion
title: Slow start and response flights
level: advanced
minutes: 3
summary: Slow start and response flights, with worked examples and explicit assumptions.
---

## Slow start

A new connection knows nothing about the path. Its **initial window** is implementation/configuration dependent. RFC 6928 experimentally permits this upper bound:

```formula
IW = min(10 × MSS, max(2 × MSS, 14,600 B))
IW = min(14,600 B, max(2,920 B, 14,600 B))
IW = 14,600 B = 10 × 1,460 B
where
IW: the initial window, the most data a new connection may send before its first ACK, in bytes (B)
MSS: maximum segment size; here 1,460 bytes
min: whichever of the values in brackets is smaller
max: whichever is larger
B: bytes
In words: this permitted upper bound is the smaller of ten segments and the larger of two segments or 14,600 bytes. For a 1,460-byte MSS it is ten segments, called IW10; sufficiently large MSS values can make the byte bound exceed 14,600.
```

It does not require every TCP to start at ten segments. Classic slow start increases cwnd on ACKs of new data, with rules affected by ACK frequency and byte-counting variants.

In the idealised model with an ACK per full segment and enough data/window capacity, each ACK adds one segment, a full window of ACKs adds a full window, and so cwnd **doubles per round**:

```formula
cwnd_k = IW × 2^k
cwnd_3 = 10 × 2^3 = 80
where
cwnd_k: the congestion window at the start of round k, in segments
IW: the initial window; here 10 segments
k: how many full rounds (round trips) have completed: 0, 1, 2 and so on
cwnd_3: the window after three rounds
In words: starting from 10 segments, the window goes 10, 20, 40, 80, doubling every round trip until ssthresh or a loss stops it.
```

Delayed ACKs, pacing, limits and different growth rules alter that approximation. "Slow" is a historical joke: it's slow compared to blasting a full window at once, but it is exponential growth.

Slow start ends when cwnd reaches the **slow start threshold** (ssthresh), or when loss is detected.

How many round trips does a short response need? First count its segments; a part-filled last segment still counts, so round up:

```formula
N = ⌈S / MSS⌉
N = ⌈100,000 B / 1,460 B⌉ = ⌈68.5⌉ = 69
10 + 20 = 30 < 69 ≤ 10 + 20 + 40 = 70
where
N: the number of segments needed
S: the response size, in bytes (B)
MSS: maximum segment size, 1,460 bytes here
⌈ ⌉: ceiling: round up to the next whole number
B: bytes
<: is less than
≤: is at most
In words: 100,000 bytes need 69 segments; two doubling flights (10 + 20) carry only 30, so a third flight is needed.
```

> [!example] Why short transfers are latency-bound
> A 100,000-byte response needs 69 payload segments at MSS 1,460. Under ideal round-based IW10 doubling, it uses three flights: 10, 20, then 39 (capacity 40). Ignoring serialization, those flights can start at the beginning, one RTT later and two RTTs later. Last-byte arrival additionally needs forward-path delay; final acknowledgement needs return delay. Three flights do not automatically mean 300 ms of extra transfer time at RTT 100 ms. This is why CDNs place servers near users and why HTTP connection reuse matters.

## Key takeaways

- Initial windows depend on implementation and configuration; the experimental IW10 rule is an upper bound.
- Ideal ACK-per-segment slow start doubles the window per completed flight.
- Count flights and path delays separately rather than equating each flight with a full extra RTT after setup.

## Further reading

- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
- [BBR: Congestion-Based Congestion Control — Google Research](https://research.google/pubs/bbr-congestion-based-congestion-control-2/)
- [RFC 3168: Explicit Congestion Notification](https://www.rfc-editor.org/rfc/rfc3168)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
- [Linux v6.12 BBRv1 implementation](https://github.com/torvalds/linux/blob/v6.12/net/ipv4/tcp_bbr.c)
- [BBRv3 IETF draft, July 2026](https://datatracker.ietf.org/doc/html/draft-ietf-ccwg-bbr-06)

- [Chiu and Jain: increase/decrease algorithms, original paper](https://pages.cs.wisc.edu/~suman/courses/740/papers/chiu89isdn.pdf)
