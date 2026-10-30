---
id: tcp-rto-backoff-ambiguity
sourceLesson: tcp-reliability
title: Timeout bounds, Karn and exponential backoff
level: intermediate
minutes: 3
summary: Timeout floors, exponential backoff and Karn's rule for ignoring ambiguous RTT samples.
---

## Bounds and measurement rules

- **Minimum RTO.** RFC 6298 says a computed value below one second SHOULD be rounded up to one second. The retrieved Linux documentation lists a **200 ms default**, with route, socket and sysctl overrides; it is not a hard universal minimum.
- **Initial RTO** before measurement: RFC 6298 recommends one second and permits a more conservative value.
- **Exponential RTO backoff.** Each time the timer fires for the same data, the RTO doubles (an optional RFC 6298 maximum must be at least 60 s; the retrieved Linux default maximum is 120 s and is configurable). This stops a sender hammering a path that is down.
- **Karn's algorithm.** Without a mechanism that disambiguates the measurement, do not take an RTT sample from retransmitted data: when the ACK arrives you can't tell whether it acknowledges the original or the copy. Negotiated timestamp echo rules can remove this ambiguity and permit such samples; the echo is selected by those rules, not invariably from the latest segment that triggered an ACK.

Exponential RTO backoff adds up quickly. With a 300 ms starting timeout and no floor or cap getting in the way, the waits are 0.3, 0.6, 1.2 and 2.4 seconds, so the fourth retransmission leaves 4.5 seconds after the original, and each new wait is longer than all the previous waits put together. A packet capture of a dead path shows this signature: the same segment resent with gaps that double each time.

A timeout delays recovery. Under RFC 5681, the TCP loss window after an RTO is at most one full-sized segment; this is a congestion-window change, not a specified one-segment-per-second rate. TCP keeps trying for a long time before it gives up: Linux's `tcp_retries2` default of 15 corresponds to a hypothetical timeout of about 924.6 seconds (over 15 minutes), which its documentation describes as a minimum for the effective timeout. Actual failure time depends on timers, overrides and application policy. An application that must notice a dead peer within seconds needs its own deadline, or a per-socket limit such as Linux's `TCP_USER_TIMEOUT`, rather than waiting for TCP to abort. An entirely idle connection with no outstanding data need not discover a vanished peer at all without probes or keepalives.

## Key takeaways

- RTO floors, caps and failure policy are specified or implementation-dependent rules beyond the raw estimate.
- Karn excludes ambiguous RTT samples unless a mechanism such as valid timestamp echoes disambiguates them.
- Repeated expiry doubles each wait, so TCP can take many minutes to abandon a dead path; applications needing faster detection set their own deadlines.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
