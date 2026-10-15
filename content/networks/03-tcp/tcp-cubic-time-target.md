---
id: tcp-cubic-time-target
sourceLesson: tcp-congestion
title: CUBIC targets, growth and coexistence
level: advanced
minutes: 4
summary: CUBIC targets, growth and coexistence, with worked examples and explicit assumptions.
---

## CUBIC: grow by the clock, not the ACK

**CUBIC** ([RFC 9438](https://www.rfc-editor.org/rfc/rfc9438)) is widely implemented; the actual default is chosen by the operating system, version and configuration. It makes two changes.

First, a gentler cut: its congestion-event reduction normally keeps **70%** of the window (a factor of 0.7, written β in the formula below); recovery and RTO handling require additional rules. It does not reduce independently for every lost packet.

Second, after a loss it grows cwnd as a **cubic function of time since the loss**, to define a target, with actual window updates still driven by ACK processing:

```formula
W(t) = C(t − K)^3 + W_max
K = ∛((W_max(1 − β)) / C)
where
W(t): CUBIC's target congestion window t seconds after the last reduction, in segments
t: time since the reduction, in seconds (s)
C: a scaling constant, 0.4 in RFC 9438 with window measured in segments and elapsed time in seconds; its numerical unit is segments per cubic second, setting the curve's aggressiveness
K: the time, in seconds, at which the curve climbs back to W_max
W_max: the congestion window just before the last reduction, in segments
β: beta, the multiplicative decrease factor, 0.7: after a congestion event the window drops to β W_max
∛: cube root: the number that gives the value inside when three copies of it are multiplied together (∛8 = 2, because 2 × 2 × 2 = 8)
In words: after a cut, the target climbs quickly, levels off as it nears the old maximum at time K, then climbs ever faster beyond it.
```

At the moment of reduction, the cube-root definition makes the cubic target equal to the retained fraction of the previous maximum. In this simplified epoch, K is where the pure cubic target reaches W_max. Actual behaviour also includes the Reno-friendly estimate, fast convergence, ACK updates and exclusion of application-limited periods. The curve is fast when far below W_max, flattens as it approaches the old limit (where loss happened last time), then accelerates again to probe for new bandwidth.

For example, after a loss at 100 segments, the window drops to 70 and the plateau comes about 4.2 s later:

```formula
W(0) = 0.7 × 100 = 70
K = ∛(100 × 0.3 / 0.4) = ∛75 ≈ 4.217 s
W(1) = 0.4 × (1 − 4.217)^3 + 100
W(1) ≈ 0.4 × (−33.3) + 100 ≈ 86.7
where
W(0): the target window just after the loss, in segments
W(1): the target one second after the loss
K: the time at which the target returns to the old maximum of 100 segments, in seconds (s)
∛: cube root; 4.217 × 4.217 × 4.217 ≈ 75
s: seconds
≈: approximately equal to
In words: the window restarts at 70, is back to about 87 after one second, and reaches the old 100 at about 4.2 s.
```

The table continues the same calculation:

| t (s) | W(t) | Phase |
|---|---|---|
| 0 | 70.0 | just after loss |
| 1 | 86.7 | rapid regrowth |
| 2 | 95.6 | slowing |
| 4.2 | 100.0 | plateau at W_max |
| 6 | 102.3 | probing |
| 7 | 108.6 | accelerating |

Because growth depends on **elapsed time**, the cubic window target reduces dependence on ACK-round counting outside the Reno-friendly region. Similar windows do not imply equal throughput for different RTTs; CUBIC still has RTT bias. CUBIC also has a **Reno-friendly region**: if a standard Reno flow would have a larger window at this moment (common on short-RTT paths), CUBIC uses the Reno value, to improve coexistence. That model comparison is not a guarantee that every actual CUBIC flow always outperforms an actual Reno flow.

Like Reno, CUBIC is **loss-based**: it responds to congestion events, which can include ECN marks before buffers overflow. Without suitable queue management its probing can build queues. That has two costs. It fills router buffers, adding queueing delay (the performance units), and it misreads **non-queue-overflow loss** (for example Wi-Fi corruption or rate-policer drops) as congestion.

## Key takeaways

- CUBIC uses elapsed time to form a cubic target and normally retains 70% after a congestion-event reduction.
- The target flattens near the prior maximum before accelerating beyond it.
- ACK processing, the Reno-friendly estimate and coexistence rules qualify the pure curve; RTT bias remains.

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
