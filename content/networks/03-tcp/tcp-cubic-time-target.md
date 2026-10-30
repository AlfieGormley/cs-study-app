---
id: tcp-cubic-time-target
sourceLesson: tcp-congestion
title: CUBIC targets, growth and coexistence
level: advanced
minutes: 4
summary: How CUBIC grows its window by elapsed time, slowing near the old limit and then probing beyond it.
---

## CUBIC: grow by the clock, not the ACK

**CUBIC** ([RFC 9438](https://www.rfc-editor.org/rfc/rfc9438)) is widely implemented; the actual default is chosen by the operating system, version and configuration. It makes two changes.

First, a gentler cut: its congestion-event reduction normally keeps **70%** of the window (a factor of 0.7, rather than Reno's 0.5); recovery and RTO handling require additional rules. It does not reduce independently for every lost packet.

Second, after a loss it grows cwnd as a **cubic function of time since the loss**, to define a target, with actual window updates still driven by ACK processing:

```formula reference
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
In words: after a cut, the target climbs quickly, levels off as it nears the old maximum, then climbs ever faster beyond it; the bigger the old maximum, the longer the climb back takes.
```

The shape is the point. The curve is fast when far below the old maximum, flattens as it approaches the window where loss happened last time, then accelerates again to probe for new bandwidth. Actual behaviour also includes the Reno-friendly estimate, fast convergence, ACK updates and exclusion of application-limited periods.

For example, after a loss at 100 segments, the target restarts at 70 and returns to the old maximum about 4.2 seconds later. With RFC 9438's constants it evolves like this:

| Time since loss (s) | Target window (segments) | Phase |
|---|---|---|
| 0 | 70.0 | just after loss |
| 1 | 86.7 | rapid regrowth |
| 2 | 95.6 | slowing |
| 4.2 | 100.0 | plateau at the old maximum |
| 6 | 102.3 | probing |
| 7 | 108.6 | accelerating |

> [!analogy] Real-world analogy: A go-kart driver finding the limit on a bend
> On a practice track, a karter who slid wide on a bend at 100 km/h takes it at 70 next lap. Over the following laps they get back towards 90 quickly, then creep up very gradually through the 95–100 range where they slid, and only once that holds do they try faster again.
>
> **How it maps:** The speed where they slid is the window at the last congestion event; dropping to 70 is CUBIC's 0.7 reduction; the quick regrowth, the careful plateau near the old limit and the accelerating probe beyond it are the two halves of the cubic curve.
>
> **Where it stops:** A karter adjusts by feel, but CUBIC follows a fixed function of elapsed time since the last reduction. And the track does not change, whereas competing flows mean the "safe" window on a network can move up or down at any moment.

Because growth depends on **elapsed time**, the cubic window target reduces dependence on ACK-round counting outside the Reno-friendly region. Similar windows do not imply equal throughput for different RTTs; CUBIC still has RTT bias. CUBIC also has a **Reno-friendly region**: if a standard Reno flow would have a larger window at this moment (common on short-RTT paths), CUBIC uses the Reno value, to improve coexistence. That model comparison is not a guarantee that every actual CUBIC flow always outperforms an actual Reno flow.

Like Reno, CUBIC is **loss-based**: it responds to congestion events, which can include ECN marks before buffers overflow. Without suitable queue management its probing can build queues. That has two costs. It fills router buffers, adding queueing delay (the performance units), and it misreads **non-queue-overflow loss** (for example Wi-Fi corruption or rate-policer drops) as congestion.

## Key takeaways

- CUBIC uses elapsed time to form a cubic target and normally retains 70% after a congestion-event reduction.
- The target flattens near the prior maximum before accelerating beyond it.
- ACK processing, the Reno-friendly estimate and coexistence rules qualify the pure curve; RTT bias remains.

## Further reading

- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
