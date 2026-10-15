---
id: tcp-congestion-window-model
sourceLesson: tcp-congestion
title: Congestion collapse and the sender window
level: advanced
minutes: 3
summary: Congestion collapse and the sender window, with worked examples and explicit assumptions.
---

In October 1986, throughput between Lawrence Berkeley Laboratory and UC Berkeley, 400 yards apart, fell from 32 kbit/s to **40 bit/s**, a factor of 800. Jacobson and Karels attributed much of the problem to transport implementations’ response to congestion: when packets were lost, senders retransmitted aggressively, which caused more loss, which caused more retransmissions. The network was busy carrying copies of packets that would be dropped anyway. This was **congestion collapse**.

Van Jacobson's 1988 fix, still at the heart of TCP, is that each sender must **infer** how much the network can take and back off when it is overloaded. Signals include ACK progress, losses, delays and, when deployed, explicit congestion marks from routers.

## The congestion window

The sender keeps a second window alongside the receiver's rwnd: the **congestion window** (cwnd), a sender-side limit on outstanding data derived from its congestion-control policy, not a direct measurement of network storage. In a simplified steady-state model, new-data sending respects whichever of cwnd and rwnd is smaller; recovery, probes, pacing and earlier in-flight data require more detailed accounting.

For a continuously backlogged, window-limited flow under stable conditions, the sender delivers about one congestion window per round trip:

```formula
X ≈ cwnd / RTT
X ≈ 100 × 1,460 B / (0.05 s)
X ≈ 2,920,000 B/s ≈ 23.4 Mbit/s
where
X: the sending rate, in bytes per second (B/s) or megabits per second (Mbit/s)
cwnd: the congestion window, in bytes; here 100 segments of 1,460 bytes
RTT: round-trip time, in seconds (s); 50 ms is 0.05 s
B/s: bytes per second
Mbit/s: megabits per second; multiply bytes per second by 8 and divide by a million
≈: approximately equal to
In words: a 100-segment window over a 50 ms round trip moves about 23 Mbit/s; double the window or halve the RTT and the rate doubles.
```

Congestion control is the set of rules for growing and shrinking cwnd. Every algorithm answers the same three questions:

1. How fast do I grow when things look fine?
2. What counts as a congestion signal?
3. How much do I shrink when I see one?

## Key takeaways

- Congestion collapse can keep a network busy while useful delivery falls sharply.
- The congestion window is a sender policy limit; the receive window reflects receiver acceptance.
- Window divided by RTT estimates a backlogged, window-limited steady rate under explicit assumptions.

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
