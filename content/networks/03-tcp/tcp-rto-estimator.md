---
id: tcp-rto-estimator
sourceLesson: tcp-reliability
title: Estimating RTT variation and timeout
level: intermediate
minutes: 5
summary: Estimating RTT variation and timeout, with worked examples and explicit assumptions.
---

## The retransmission timeout (RTO)

The last line of defence is a timer. RFC 6298’s timer starts when outstanding data needs timing, restarts on an ACK acknowledging new data, and stops when all outstanding data is acknowledged. On expiry, the earliest unacknowledged segment is retransmitted. Thus expiry is not always exactly one RTO after that segment’s original send.

The RTO must be somewhat longer than a typical round trip, but RTTs vary from microseconds in a data centre to seconds on a satellite link, and they change during a connection. So TCP **measures** them. [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298) defines the calculation, which Van Jacobson introduced in 1988.

It keeps two running averages: a smoothed RTT (SRTT), its best guess at the typical round trip, and an RTT variation (RTTVAR), how much the samples usually stray from that guess. With no history, the first measurement sets both:

```formula
SRTT = R
RTTVAR = R / 2
where
SRTT: smoothed round-trip time, TCP's running average of the RTT, in milliseconds (ms)
RTTVAR: round-trip time variation, a running average of how far samples stray from SRTT, in ms
R: the first measured RTT sample, in ms
ms: milliseconds, thousandths of a second
In words: with only one measurement, use it as the average and assume it might be off by half its size.
```

Each later sample nudges both averages towards the new evidence. This kind of update is an **exponentially weighted moving average** (EWMA): keep most of the old value and blend in a small share of the new one.

```formula
RTTVAR_new = (1 − β)RTTVAR
           + β |SRTT − R|
SRTT_new = (1 − α)SRTT + αR
where
RTTVAR_new: the updated variation, in milliseconds (ms)
RTTVAR: the variation before this sample
SRTT_new: the updated smoothed RTT, in ms
SRTT: the smoothed RTT before this sample (the old value, also used in the RTTVAR line)
R: the new RTT sample, in ms
α: alpha, the share of the new sample blended into SRTT; RFC 6298 uses 1/8 = 0.125
β: beta, the share of the new deviation blended into RTTVAR; RFC 6298 uses 1/4 = 0.25
|SRTT − R|: the absolute value of the difference: its size, ignoring the sign, so |100 − 120| = 20
ms: milliseconds
In words: each new sample moves SRTT one eighth of the way towards it, and moves RTTVAR a quarter of the way towards how surprising the sample was.
```

RTTVAR is updated **before** SRTT, using the old SRTT. The timeout then adds a safety margin of four variations to the average:

```formula
RTO = SRTT + max(G, 4 RTTVAR)
where
RTO: retransmission timeout, how long to wait for an ACK before resending, in milliseconds (ms)
SRTT: the smoothed round-trip time, in ms
RTTVAR: the round-trip time variation, in ms
G: the clock granularity: the tick size of the system's timer, for example 1 ms; it stops the margin rounding down to zero
max: whichever of the two values in brackets is larger
ms: milliseconds
In words: wait for the typical round trip plus four times its usual wobble, so a steady path gets a tight timeout and a jittery one a generous margin.
```

A worked example with two samples, ignoring the minimum RTO floor and assuming the clock granularity is below 4 × RTTVAR:

```formula
SRTT_1 = 100 ms
RTTVAR_1 = (100 ms) / 2 = 50 ms
RTO_1 = 100 ms + 4 × 50 ms = 300 ms
RTTVAR_2 = 0.75 × 50 ms
         + 0.25 × |100 ms − 120 ms|
RTTVAR_2 = 37.5 ms + 5 ms = 42.5 ms
SRTT_2 = 0.875 × 100 ms + 0.125 × 120 ms
SRTT_2 = 87.5 ms + 15 ms = 102.5 ms
RTO_2 = 102.5 ms + 4 × 42.5 ms
RTO_2 = 102.5 ms + 170 ms = 272.5 ms
where
SRTT_1: the smoothed RTT after the first sample (100 ms), in milliseconds (ms)
RTTVAR_1: the variation after the first sample
RTO_1: the retransmission timeout after the first sample
RTTVAR_2: the variation after the second sample (120 ms); 0.75 is 1 − 1/4, 0.25 is 1/4, and |100 − 120| is the size of the difference ignoring its sign, 20
SRTT_2: the smoothed RTT after the second sample; 0.875 is 1 − 1/8 and 0.125 is 1/8
RTO_2: the retransmission timeout after the second sample
ms: milliseconds
In words: a slightly slower second sample nudges the average up to 102.5 ms but shrinks the variation, so the timeout falls from 300 ms to 272.5 ms.
```

The 4 × RTTVAR term is the important one. A connection with a steady RTT gets a tight timeout; a jittery one gets a generous margin, so it doesn't fire on every delay spike.

## Key takeaways

- RFC 6298 smooths both RTT and the size of sample deviations.
- Update variation using the old smoothed RTT before updating the smoothed RTT itself.
- The raw estimator adds the larger of clock granularity and four variations; floors and timer policy apply separately.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [RFC 2018: TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018)
- [RFC 8985: The RACK-TLP Loss Detection Algorithm for TCP](https://www.rfc-editor.org/rfc/rfc8985)
- [RFC 5681: TCP Congestion Control (fast retransmit)](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
- [Linux retransmission timer controls](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
