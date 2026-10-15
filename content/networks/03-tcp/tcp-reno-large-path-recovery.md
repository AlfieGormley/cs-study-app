---
id: tcp-reno-large-path-recovery
sourceLesson: tcp-congestion
title: Reno recovery on a large-delay path
level: advanced
minutes: 3
summary: Reno recovery on a large-delay path, with worked examples and explicit assumptions.
---

## Why Reno fails on fast, long paths

Additive increase is one segment per RTT, no matter how big the window. Consider a model counting 1,500 payload bytes per segment, ignoring headers, at 10 Gbit/s and 100 ms RTT. First the window needed, then the time to win back half of it at one segment per round trip:

```formula
W = R RTT / (S × 8)
W = 10^10 bit/s × 0.1 s / (12,000 bit)
W ≈ 83,333
T_rec = (W / 2) × RTT
T_rec = 41,667 × 0.1 s ≈ 4,167 s ≈ 69 min
where
W: the congestion window needed to fill the path, in segments
R: the target rate; 10 Gbit/s is 10^10 bits per second (bit/s)
RTT: round-trip time, in seconds (s); 100 ms is 0.1 s
S: payload bytes per segment, 1,500; × 8 turns it into 12,000 bits
T_rec: the time to grow back from W / 2 to W at one segment per RTT
bit: binary digit; 8 bits make a byte
s: seconds
min: minutes
≈: approximately equal to
In words: a 10 Gbit/s, 100 ms path needs about 83,000 segments in flight, and after one halving Reno needs over an hour of loss-free round trips to get back.
```

After one loss halves the window, getting back to W takes about 41,667 RTTs: **over an hour**, during which a single further loss starts the climb again. In the distinct average-window model in RFC 3649, sustaining this average rate requires roughly one congestion event per five billion packets ([RFC 3649](https://www.rfc-editor.org/rfc/rfc3649)). This illustrates Reno’s scaling limitation under the stated assumptions, not an absolute impossibility for every high-speed path or workload.

## Key takeaways

- Large bandwidth-delay products need large in-flight windows.
- One-segment-per-RTT Reno growth can take over an hour to undo one halving in the stated 10 Gbit/s model.
- This comparison is a scaling illustration rather than a universal performance prediction.

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
