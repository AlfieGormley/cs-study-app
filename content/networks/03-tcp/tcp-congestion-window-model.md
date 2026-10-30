---
id: tcp-congestion-window-model
sourceLesson: tcp-congestion
title: Congestion collapse and the sender window
level: advanced
minutes: 3
summary: Why the Internet once collapsed under retransmissions, and how the congestion window keeps senders in check.
---

In October 1986, throughput between Lawrence Berkeley Laboratory and UC Berkeley, 400 yards apart, fell from 32 kbit/s to **40 bit/s**, a factor of 800. Jacobson and Karels attributed much of the problem to transport implementations’ response to congestion: when packets were lost, senders retransmitted aggressively, which caused more loss, which caused more retransmissions. The network was busy carrying copies of packets that would be dropped anyway. This was **congestion collapse**.

> [!analogy] Real-world analogy: Everyone redialling after a busy tone
> After a big event, everyone tries to phone home at once. Calls fail, so everyone immediately redials, and the redials add to the load. Soon the exchange spends its effort on attempts that cannot succeed, and fewer calls get through than if people had waited a moment.
>
> **How it maps:** Each redial is an aggressive TCP retransmission; the jammed exchange is the overloaded router queue dropping packets; the falling number of completed calls is the collapse in useful throughput. Jacobson's fix is the equivalent of each caller waiting longer after every failure and starting gently when lines clear.
>
> **Where it stops:** Callers can hear a busy tone, but a TCP sender gets no direct signal and has to infer congestion from missing or marked ACKs. And the telephone network can refuse new calls centrally, whereas the Internet relies on every sender restraining itself.

Van Jacobson's 1988 fix, still at the heart of TCP, is that each sender must **infer** how much the network can take and back off when it is overloaded. Signals include ACK progress, losses, delays and, when deployed, explicit congestion marks from routers.

## The congestion window

The sender keeps a second window alongside the receiver's rwnd: the **congestion window** (cwnd), a sender-side limit on outstanding data derived from its congestion-control policy, not a direct measurement of network storage. In a simplified steady-state model, new-data sending respects whichever of cwnd and rwnd is smaller; recovery, probes, pacing and earlier in-flight data require more detailed accounting.

For a continuously backlogged, window-limited flow under stable conditions, the sender delivers about one congestion window per round trip. That is the same window/RTT relationship as for the receive window, with cwnd as the limit:

```formula reference
X ≈ cwnd / RTT
where
X: the sending rate, in bytes per second (B/s)
cwnd: the congestion window, in bytes
RTT: round-trip time, in seconds (s)
B/s: bytes per second
≈: approximately equal to
In words: a congestion-window-limited sender delivers about one window per round trip, so doubling the window or halving the round trip roughly doubles the rate.
```

For example, a 100-segment window of 1,460-byte segments over a 50 ms round trip moves about 23 Mbit/s. Two consequences follow. Congestion control changes the rate by changing the window. And if the round trip changes, say after a route change or a growing queue, the rate changes too, even though the window has not.

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
- [TCP congestion control — Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_control)
