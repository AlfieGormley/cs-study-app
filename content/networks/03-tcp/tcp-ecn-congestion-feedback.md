---
id: tcp-ecn-congestion-feedback
sourceLesson: tcp-congestion
title: ECN marks, DCTCP and sender selection
level: advanced
minutes: 3
summary: How ECN signals congestion by marking packets instead of dropping them, and how DCTCP scales its response.
---

## ECN: congestion without loss

Loss-oriented algorithms can also react to explicit congestion indications. **Explicit Congestion Notification** ([RFC 3168](https://www.rfc-editor.org/rfc/rfc3168)) lets a router **mark** a packet instead of dropping it:

1. In classic TCP ECN (RFC 3168), both sides negotiate ECN capability in the handshake. Later ECN schemes have different feedback details.
2. Packets are sent with an ECN-capable codepoint in the IP header.
3. A capable queue-management algorithm may set **CE** (Congestion Experienced) on eligible packets instead of dropping; overload and policy can still cause drops.
4. The receiver echoes it with **ECE** in its ACKs; the sender reduces cwnd as for a loss and replies with **CWR**.

A delivered CE-marked packet does not need retransmission merely because it was marked. ECN does not prevent unrelated loss or guarantee a one-RTT improvement. Data-centre algorithms such as **DCTCP** ([RFC 8257](https://www.rfc-editor.org/rfc/rfc8257)) go further, scaling the reduction by the **fraction** of marked packets to keep queues tiny:

```formula reference
α_new = (1 − g)α + gM
cwnd_new = cwnd(1 − α_new / 2)
where
α: alpha, DCTCP's running estimate of the fraction of data that is being marked, from 0 to 1
α_new: the updated estimate after one window of data
g: the weight given to the newest measurement, between 0 and 1; RFC 8257 notes that 1/16 is used in some implementations
M: the fraction of bytes acknowledged in the last window of data that carried a CE mark
cwnd: the congestion window before the reduction
cwnd_new: the window after the reduction
In words: DCTCP keeps a running average of the fraction of its data that was marked; if almost nothing is marked it cuts the window only a little, and if everything is marked it halves the window like Reno.
```

So DCTCP's response is graded: a queue that exceeds the switch's marking threshold only briefly produces few marks and a small trim rather than a halving, which lets data-centre switches keep their queues short.

> [!analogy] Real-world analogy: A "kitchen busy" sticker instead of a thrown-away order
> A busy kitchen could cope with overload by throwing some orders away, and the waiter would learn of the problem only when a customer complained. Instead, the kitchen puts a "kitchen busy" sticker on plates it still serves, and the waiter, seeing the stickers, takes orders more slowly.
>
> **How it maps:** Throwing orders away is a router dropping packets; the sticker is the CE mark on a packet that is still delivered; the waiter noticing it is the receiver echoing ECE to the sender, which reduces its congestion window. DCTCP is a waiter who slows down in proportion to how many plates carry stickers.
>
> **Where it stops:** The waiter sees the sticker straight away, whereas the mark reaches the sender only through the receiver's ACKs, about a round trip later. And marking works only when both endpoints negotiate ECN, the congested router supports it and devices along the path leave the ECN bits intact; otherwise the router copes by dropping.

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

- [RFC 3168: Explicit Congestion Notification](https://www.rfc-editor.org/rfc/rfc3168)
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
