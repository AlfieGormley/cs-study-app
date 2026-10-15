---
id: tcp-ecn-congestion-feedback
sourceLesson: tcp-congestion
title: ECN marks, DCTCP and sender selection
level: advanced
minutes: 3
summary: ECN marks, DCTCP and sender selection, with worked examples and explicit assumptions.
---

## ECN: congestion without loss

Loss-oriented algorithms can also react to explicit congestion indications. **Explicit Congestion Notification** ([RFC 3168](https://www.rfc-editor.org/rfc/rfc3168)) lets a router **mark** a packet instead of dropping it:

1. In classic TCP ECN (RFC 3168), both sides negotiate ECN capability in the handshake. Later ECN schemes have different feedback details.
2. Packets are sent with an ECN-capable codepoint in the IP header.
3. A capable queue-management algorithm may set **CE** (Congestion Experienced) on eligible packets instead of dropping; overload and policy can still cause drops.
4. The receiver echoes it with **ECE** in its ACKs; the sender reduces cwnd as for a loss and replies with **CWR**.

A delivered CE-marked packet does not need retransmission merely because it was marked. ECN does not prevent unrelated loss or guarantee a one-RTT improvement. Data-centre algorithms such as **DCTCP** ([RFC 8257](https://www.rfc-editor.org/rfc/rfc8257)) go further, scaling the reduction by the **fraction** of marked packets to keep queues tiny:

```formula
α_new = (1 − g)α + gM
cwnd_new = cwnd(1 − α_new / 2)
where
α: alpha, DCTCP's running estimate of the fraction of data that is being marked, from 0 to 1
α_new: the updated estimate after one window of data
g: the weight given to the newest measurement, between 0 and 1; RFC 8257 notes that 1/16 is used in some implementations
M: the fraction of bytes acknowledged in the last window of data that carried a CE mark
cwnd: the congestion window before the reduction
cwnd_new: the window after the reduction
In words: if almost nothing is marked, cut the window only a little; if every packet is marked (α = 1), halve it like Reno.
```


## Choosing and checking

Example Linux inspection commands (shown output is illustrative, not a guaranteed default):

```
$ sysctl net.ipv4.tcp_congestion_control
net.ipv4.tcp_congestion_control = cubic
$ ss -ti   # per-connection cwnd, rtt
```

An application can choose per socket with the `TCP_CONGESTION` option. Congestion control runs on the **sender**, so a server can change its TCP sender algorithm without requiring the client to use the same algorithm. Whether performance improves must be measured; receiver feedback and available implementation support still matter.

## Key takeaways

- Classic ECN negotiates capability and echoes delivered CE marks using TCP flags.
- A mark signals congestion without making the marked packet itself require retransmission.
- DCTCP scales a reduction using a smoothed marked-data fraction; sender algorithm selection remains implementation-dependent.

## Further reading

- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
- [BBR: Congestion-Based Congestion Control — Google Research](https://research.google/pubs/bbr-congestion-based-congestion-control-2/)
- [RFC 3168: Explicit Congestion Notification](https://www.rfc-editor.org/rfc/rfc3168)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
- [Linux v6.12 BBRv1 implementation](https://github.com/torvalds/linux/blob/v6.12/net/ipv4/tcp_bbr.c)
- [BBRv3 IETF draft, July 2026](https://datatracker.ietf.org/doc/html/draft-ietf-ccwg-bbr-06)

> [!note] Content omitted after review
> Universal operating-system defaults, guaranteed equal-share fairness and fixed BBR speedups are omitted because this review did not establish suitable versioned measurements. Congestion-control traces here are explicit models, not packet-level benchmarks.

- [Chiu and Jain: increase/decrease algorithms, original paper](https://pages.cs.wisc.edu/~suman/courses/740/papers/chiu89isdn.pdf)
