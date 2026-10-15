---
id: tcp-rto-backoff-ambiguity
sourceLesson: tcp-reliability
title: Timeout bounds, Karn and exponential backoff
level: intermediate
minutes: 3
summary: Timeout bounds, Karn and exponential backoff, with worked examples and explicit assumptions.
---

## Bounds and measurement rules

- **Minimum RTO.** RFC 6298 says a computed value below one second SHOULD be rounded up to one second. The retrieved Linux documentation lists a **200 ms default**, with route, socket and sysctl overrides; it is not a hard universal lower bound.
- **Initial RTO** before measurement: RFC 6298 recommends one second and permits a more conservative value.
- **Exponential RTO backoff.** Each time the timer fires for the same data, the RTO doubles (an optional RFC 6298 maximum must be at least 60 s; the retrieved Linux default maximum is 120 s and is configurable). This stops a sender hammering a path that is down.
- **Karn's algorithm.** Without a mechanism that disambiguates the measurement, do not take an RTT sample from retransmitted data: when the ACK arrives you can't tell whether it acknowledges the original or the copy. Negotiated timestamp echo rules can remove this ambiguity and permit such samples; the echo is selected by those rules, not invariably from the latest segment that triggered an ACK.

Exponential RTO backoff adds up quickly. If each wait doubles, the total time from the original send to the k-th retransmission is a doubling series:

```formula
T_k = RTO_0 × (1 + 2 + … + 2^{k − 1})
T_k = RTO_0 × (2^k − 1)
T_4 = 0.3 s × (16 − 1) = 4.5 s
where
T_k: the time from the original transmission to the k-th retransmission, in seconds (s)
RTO_0: the timeout before any RTO backoff; here 300 ms = 0.3 s
k: which retransmission we mean: 1, 2, 3 and so on
T_4: the same total for the fourth retransmission
…: and so on, continuing the pattern
s: seconds
In words: with a 300 ms starting timeout, the waits are 0.3, 0.6, 1.2 and 2.4 s, so the fourth retransmission goes out 4.5 s after the original.
```

A timeout delays recovery. Under RFC 5681, the TCP loss window after an RTO is at most one full-sized segment; this is a congestion-window change, not a specified one-segment-per-second rate. Linux documents `tcp_retries2 = 15` using a hypothetical default timeout of 924.6 seconds as a minimum under its stated RTO backoff model. Actual failure time depends on timers, overrides and application policy. An entirely idle connection with no outstanding data need not discover a vanished peer without probes or keepalives.

## Key takeaways

- RTO floors, caps and failure policy are specified or implementation-dependent rules beyond the raw estimate.
- Karn excludes ambiguous RTT samples unless a mechanism such as valid timestamp echoes disambiguates them.
- Repeated expiry doubles waits, so total elapsed time is a geometric sum.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
