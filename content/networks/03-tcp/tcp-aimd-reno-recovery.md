---
id: tcp-aimd-reno-recovery
sourceLesson: tcp-congestion
title: AIMD and Reno recovery rules
level: advanced
minutes: 4
summary: Additive increase, multiplicative decrease, and how Reno reacts differently to duplicate ACKs and timeouts.
---

## Congestion avoidance: AIMD

In classic Reno congestion avoidance, the sender probes with approximately **one MSS of cwnd growth per RTT** under ideal ACK/traffic assumptions. Crossing ssthresh does not prove that the path is currently near capacity. That is **additive increase**.

When loss signals congestion, cwnd is cut by a **fraction**: **multiplicative decrease**.

```formula reference
W_up = W + a
W_down = bW
where
W: the congestion window now, in segments
W_up: the window one round trip later when no congestion was seen (additive increase)
a: how much is added per round trip; 1 segment for Reno
W_down: the window just after a congestion signal (multiplicative decrease)
b: the fraction kept after a cut; 0.5 for Reno, 0.7 for CUBIC
In words: grow by a fixed step each round trip, and cut to a fixed fraction on congestion; a Reno window of 40 segments grows to 41 or is cut to 20.
```

Together, **AIMD** has an important property, shown by Chiu and Jain in 1989: in a simplified synchronous feedback model with comparable flows, rates can converge toward equal shares. Real TCP fairness depends on RTTs, loss/mark patterns, starting times, bottlenecks and algorithm variants. Each increase adds the same amount to both; each decrease takes more from the larger. Over many cycles the difference shrinks.

## Reno: reacting to two kinds of loss

TCP Reno ([RFC 5681](https://www.rfc-editor.org/rfc/rfc5681)) treats the two loss signals from the reliability units differently:

- **Three qualifying duplicate ACKs**: classic fast retransmit enters TCP fast recovery. RFC 5681 sets ssthresh to at most half the data in flight (FlightSize), but never below two segments; that is not universally half of cwnd. Reno temporarily inflates cwnd by three segments, with further duplicate-ACK handling, then deflates on a recovery-completing ACK. The simplified trace below shows only the post-recovery reduction.
- **Retransmission timeout**: on the first RTO retransmission of that data, apply the threshold rule; set the TCP loss window to at most one full-sized segment and resume slow start. A repeated RTO for the same data does not repeatedly halve ssthresh under the RFC rule. Loss/timeout observations do not prove “mild congestion” or “nothing is getting through”.

Put side by side for a Reno sender with 40 full-sized segments in flight:

| Signal | ssthresh | cwnd next | Then |
|---|---|---|---|
| 3 duplicate ACKs | about 20 | about 20 after recovery | +1 segment per RTT |
| RTO (first expiry) | about 20 | 1 segment | slow start up to 20 |

The duplicate-ACK path keeps sending at about half the old rate because ACKs show data is still getting through; the timeout path starts again from one segment because the sender has lost its ACK clock. During fast recovery Reno temporarily adds three segments for the packets that the duplicate ACKs show have left the network, then deflates when recovery completes.

> [!analogy] Real-world analogy: Sharing a narrow road
> Drivers on a shared road each speed up gently while it is clear, and brake hard to about half speed when they see brake lights ahead. A driver going faster loses more speed in each braking, while everyone gains speed at the same gentle rate, so over many slowdowns their speeds drift together.
>
> **How it maps:** Gentle acceleration is additive increase of one segment per round trip; braking to about half speed is the multiplicative decrease after a congestion signal; drifting towards similar speeds is the Chiu–Jain result that AIMD flows move towards fairer shares.
>
> **Where it stops:** Drivers see the traffic directly, but TCP senders learn of congestion only from lost or marked packets a round trip later. And flows with longer round trips accelerate more slowly in TCP, so real shares also depend on RTT.

Its predecessor, Tahoe, reset to one segment on every loss. **NewReno** ([RFC 6582](https://www.rfc-editor.org/rfc/rfc6582)) fixes Reno's handling of several losses in one window; SACK supplies additional received-range information, but limited reports, reordering and receiver reneging still require a loss-recovery algorithm.

## Key takeaways

- AIMD combines additive probing with fractional reductions; equal shares require model assumptions.
- RFC 5681 recovery thresholds depend on FlightSize and a two-segment lower floor for that ceiling.
- Fast recovery temporarily inflates the window; an RTO invokes a loss window of at most one segment.

## Further reading

- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [Chiu and Jain: increase/decrease algorithms, original paper](https://pages.cs.wisc.edu/~suman/courses/740/papers/chiu89isdn.pdf)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
