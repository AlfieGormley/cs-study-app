---
id: tcp-slow-start-flights
sourceLesson: tcp-congestion
title: Slow start and response flights
level: advanced
minutes: 3
summary: How a new connection starts small and doubles its window each round trip until it finds a limit.
---

## Slow start

A new connection knows nothing about the path. Its **initial window** is implementation/configuration dependent. RFC 6928 experimentally permits this ceiling:

```formula reference
IW = min(10 × MSS, max(2 × MSS, 14,600 B))
where
IW: the initial window, the most data a new connection may send before its first ACK, in bytes (B)
MSS: maximum segment size, the most payload one segment carries; 1,460 bytes is typical on Ethernet
min: whichever of the values in brackets is smaller
max: whichever is larger
B: bytes
In words: a new connection may start with up to ten segments, capped at 14,600 bytes unless two segments are larger than that; for a typical 1,460-byte MSS this is ten segments, the common ceiling called IW10.
```

It does not require every TCP to start at ten segments. Classic slow start increases cwnd on ACKs of new data, with rules affected by ACK frequency and byte-counting variants.

In the idealised model with an ACK per full segment and enough data/window capacity, each ACK adds one segment, so a full window of ACKs adds a full window and cwnd **doubles per round trip**: 10, 20, 40, 80 segments, and so on. Delayed ACKs, pacing, limits and different growth rules alter that approximation. "Slow" is a historical joke: it's slow compared to blasting a full window at once, but it is exponential growth.

Slow start ends when cwnd reaches the **slow start threshold** (ssthresh), or when loss is detected. In a trace, that shows up as doubling that suddenly changes to slow, steady growth (at ssthresh) or a sharp cut (after a loss).

> [!analogy] Real-world analogy: A new café ordering cakes
> A new café has no idea how many cakes it can sell. It orders 10; they all sell, so it orders 20, then 40, doubling while every batch sells out. The first time cakes are left over, it stops doubling and adds just one cake a day.
>
> **How it maps:** Each batch is a slow-start round, and "all sold" is the ACKs reporting that the whole flight was delivered, which doubles the window. The first leftovers are the signal that ends doubling; in TCP that signal is reaching the slow start threshold (or detecting a loss), after which growth slows to about one segment per round trip: congestion avoidance.
>
> **Where it stops:** The café learns once a day, whereas TCP grows a little with each ACK as it arrives, so real traces are smoother. And a real packet loss does more than end the doubling: TCP also cuts its window, and the lost data must be detected and resent.

> [!example] Why short transfers are latency-bound
> A 100,000-byte response needs 69 payload segments at MSS 1,460. Under ideal round-based IW10 doubling, it uses three flights: 10, 20, then 39 (capacity 40). Ignoring serialization, those flights can start at the beginning, one RTT later and two RTTs later. Last-byte arrival additionally needs forward-path delay; final acknowledgement needs return delay. Three flights do not automatically mean 300 ms of extra transfer time at RTT 100 ms. This is why CDNs place servers near users and why HTTP connection reuse matters.

## Key takeaways

- Initial windows depend on implementation and configuration; the experimental IW10 rule is a ceiling, not a requirement.
- Ideal ACK-per-segment slow start doubles the window per completed flight.
- Count flights and path delays separately rather than equating each flight with a full extra RTT after setup.

## Further reading

- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
