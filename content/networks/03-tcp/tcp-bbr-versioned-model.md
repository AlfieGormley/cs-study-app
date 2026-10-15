---
id: tcp-bbr-versioned-model
sourceLesson: tcp-congestion
title: BBRv1 bandwidth and RTT estimation
level: advanced
minutes: 4
summary: BBRv1 bandwidth and RTT estimation, with worked examples and explicit assumptions.
---

## BBR: model the path

Google's **BBR** (Bottleneck Bandwidth and Round-trip propagation time, 2016) takes a different approach: it estimates path properties from delivery feedback and controls pacing/in-flight data from a model. The numerical details below describe **BBRv1 as implemented in Linux v6.12**, not all BBR versions.

- **BtlBw**: the bottleneck bandwidth, estimated using a windowed maximum of delivery-rate samples over ten packet-timed rounds in this version, with safeguards for limited sending and other conditions.
- **RTprop**: the round-trip propagation delay, estimated using a ten-second windowed minimum in this version. The estimate includes endpoint/serialization effects and may include persistent queueing; it is not pure physical propagation delay.

Their product is the BDP. BBR **paces** packets at about BtlBw and caps in-flight data at a small multiple of the BDP (a base gain near 2× in BBRv1, with minimum-window adjustments, allowances for ACKs that arrive in bunches, and others):

```formula
BDP = BtlBw RTprop
R_pace = g_p BtlBw
W_cap = g_c BDP
BDP = 12,500,000 B/s × 0.02 s = 250,000 B
W_cap ≈ 2 × 250,000 B = 500,000 B
where
BDP: bandwidth-delay product, the data in flight that exactly fills the path, in bytes (B)
BtlBw: the estimated bottleneck bandwidth; here 100 Mbit/s, which is 12,500,000 bytes per second (B/s)
RTprop: the estimated round-trip propagation time; here 20 ms = 0.02 s
R_pace: the pacing rate, how fast BBR releases packets
g_p: the pacing gain for the current phase, for example 1.25, 1 or 0.75 in ProbeBW
W_cap: the cap on data in flight
g_c: the congestion-window gain, about 2 in BBRv1
s: seconds
B/s: bytes per second
≈: approximately equal to
In words: on a 100 Mbit/s path with a 20 ms base RTT, BBR aims to keep about 250 KB in the pipe and allows roughly twice that in flight.
```

The ideal operating point is to keep the pipe full without building a queue.

To observe available delivery capacity the sender must offer enough data; probing beyond it can build a queue and obscure the baseline RTT. Reducing in-flight data can help refresh the RTT estimate. These are estimation challenges, not a theorem that full utilisation always requires a queue. So BBR cycles through phases:

| Phase | Behaviour |
|---|---|
| Startup | Pacing gain about 2.89, designed for rapid growth; exits after three qualifying rounds without 25% bandwidth growth |
| Drain | Gain below 1 to empty the queue Startup built |
| ProbeBW | Gains 1.25, 0.75, then six 1.0 phases; transitions use timing/in-flight checks |
| ProbeRTT | On qualifying minimum-RTT expiry, reduce toward 4 packets; duration includes at least 200 ms and a completed round |

BBRv1 aims to keep utilisation high without persistently filling queues and can avoid repeated Reno/CUBIC-style reductions for non-congestion loss. It still performs loss recovery and includes loss-related recovery/policer handling; “ignores all loss” is false. Results depend on the path and competing traffic, so there is no guaranteed speedup or fairness outcome.

Later BBR versions change the model and loss response. The **July 2026 BBRv3 IETF draft** retrieved here remains experimental and explicitly does **not** specify a particular ECN algorithm; if a connection advertises ECN support, however, CE marks must still be treated as congestion. Thus, claims that every BBRv2/v3 implementation has one common ECN algorithm are omitted. Linux BBR uses packet pacing, via `fq` or internal pacing support in the examined implementation.

## Key takeaways

- Linux v6.12 BBRv1 estimates recent delivery capacity and minimum RTT to control pacing and in-flight limits.
- Startup, Drain, ProbeBW and ProbeRTT serve different estimation and queue-management purposes.
- BBR versions differ; neither loss handling, ECN behaviour nor fairness is universal across all versions.

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
