---
id: tcp-aimd-reno-recovery
sourceLesson: tcp-congestion
title: AIMD and Reno recovery rules
level: advanced
minutes: 4
summary: AIMD and Reno recovery rules, with worked examples and explicit assumptions.
---

## Congestion avoidance: AIMD

In classic Reno congestion avoidance, the sender probes with approximately **one MSS of cwnd growth per RTT** under ideal ACK/traffic assumptions. Crossing ssthresh does not prove that the path is currently near capacity. That is **additive increase**.

When loss signals congestion, cwnd is cut by a **fraction**: **multiplicative decrease**.

```formula
W_up = W + a
W_down = bW
where
W: the congestion window now, in segments
W_up: the window one round trip later when no congestion was seen (additive increase)
a: how much is added per round trip; 1 segment for Reno
W_down: the window just after a congestion signal (multiplicative decrease)
b: the fraction kept after a cut; 0.5 for Reno, 0.7 for CUBIC
In words: grow by a fixed step each round trip, and cut to a fixed fraction on congestion; with W = 40, Reno grows to 41 or cuts to 20.
```

Together, **AIMD** has an important property, shown by Chiu and Jain in 1989: in a simplified synchronous feedback model with comparable flows, rates can converge toward equal shares. Real TCP fairness depends on RTTs, loss/mark patterns, starting times, bottlenecks and algorithm variants. Each increase adds the same amount to both; each decrease takes more from the larger. Over many cycles the difference shrinks.

## Reno: reacting to two kinds of loss

TCP Reno ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) treats the two loss signals from the reliability units differently:

- **Three qualifying duplicate ACKs**: classic fast retransmit enters TCP fast recovery. The RFC 5681 threshold rule (formula below) is a ceiling based on FlightSize, not universally half of cwnd. Reno temporarily inflates cwnd by three segments, with further duplicate-ACK handling, then deflates on a recovery-completing ACK. The simplified trace below shows only the post-recovery reduction.
- **Retransmission timeout**: on the first RTO retransmission of that data, apply the threshold rule; set the TCP loss window to at most one full-sized segment and resume slow start. A repeated RTO for the same data does not repeatedly halve ssthresh under the RFC rule. Loss/timeout observations do not prove “mild congestion” or “nothing is getting through”.

The fast-recovery numbers, worked for 40 segments in flight:

```formula
ssthresh ≤ max(FlightSize / 2, 2 × SMSS)
ssthresh = 58,400 B / 2 = 29,200 B
cwnd = ssthresh + 3 × SMSS
cwnd = 29,200 B + 4,380 B = 33,580 B
where
ssthresh: slow start threshold, the window size at which slow start hands over to congestion avoidance, in bytes (B)
FlightSize: the data sent but not yet acknowledged when loss is detected; here 40 × 1,460 = 58,400 bytes
SMSS: sender maximum segment size, the largest segment the sender sends; here 1,460 bytes
cwnd: the congestion window during fast recovery
max: whichever of the values in brackets is larger; it keeps the ceiling at least two segments
≤: is at most
B: bytes
In words: on three duplicate ACKs, set the threshold to half of what was in flight (at most), then temporarily add three segments for the three packets the duplicate ACKs show have left the network.
```

Its predecessor, Tahoe, reset to one segment on every loss. **NewReno** ([RFC 6582](https://www.rfc-editor.org/rfc/rfc6582)) fixes Reno's handling of several losses in one window; SACK supplies additional received-range information, but limited reports, reordering and receiver reneging still require a loss-recovery algorithm.

## Key takeaways

- AIMD combines additive probing with fractional reductions; equal shares require model assumptions.
- RFC 5681 recovery thresholds depend on FlightSize and a two-segment lower floor for that ceiling.
- Fast recovery temporarily inflates the window; an RTO invokes a loss window of at most one segment.

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
