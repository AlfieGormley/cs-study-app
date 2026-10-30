---
id: tcp-rto-estimator
sourceLesson: tcp-reliability
title: Estimating RTT variation and timeout
level: intermediate
minutes: 3
summary: How TCP sets its retransmission timeout from a smoothed RTT plus a margin for jitter.
---

## The retransmission timeout (RTO)

The last line of defence is a timer. RFC 6298’s timer starts when outstanding data needs timing, restarts on an ACK acknowledging new data, and stops when all outstanding data is acknowledged. On expiry, the earliest unacknowledged segment is retransmitted. Thus expiry is not always exactly one RTO after that segment’s original send.

The RTO must be somewhat longer than a typical round trip, but RTTs vary from microseconds in a data centre to seconds on a satellite link, and they change during a connection. So TCP **measures** them. [RFC 6298](https://www.rfc-editor.org/rfc/rfc6298) defines the calculation, which Van Jacobson introduced in 1988.

It keeps two running averages: a smoothed RTT (SRTT), its best guess at the typical round trip, and an RTT variation (RTTVAR), how much the samples usually stray from that guess. With no history, the first measurement sets SRTT to that sample and RTTVAR to half of it: a cautious starting guess.

Each later sample nudges both averages towards the new evidence. This kind of update is an **exponentially weighted moving average** (EWMA): keep most of the old value and blend in a small share of the new one. RTTVAR is updated **before** SRTT, so it measures the surprise against the old average.

```formula reference
RTTVAR_new = (1 − β)RTTVAR
           + β |SRTT − R|
SRTT_new = (1 − α)SRTT + αR
where
RTTVAR_new: the updated variation, in milliseconds (ms)
RTTVAR: the variation before this sample, in ms
SRTT_new: the updated smoothed RTT, in ms
SRTT: the smoothed RTT before this sample (the old value, also used in the RTTVAR line), in ms
R: the new RTT sample, in ms
α: alpha, the share of the new sample blended into SRTT; RFC 6298 uses 1/8 = 0.125
β: beta, the share of the new deviation blended into RTTVAR; RFC 6298 uses 1/4 = 0.25
|SRTT − R|: the absolute value of the difference: its size, ignoring the sign, so |100 − 120| = 20
ms: milliseconds, thousandths of a second
In words: each new RTT sample moves the smoothed RTT an eighth of the way towards it, and moves the variation a quarter of the way towards how far that sample was from the old smoothed RTT.
```

The timeout then adds a safety margin of four variations to the average. This is the relationship worth remembering:

```formula essential
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

## What moves the timeout

The 4 × RTTVAR margin usually matters more than the average itself:

- **A steady path.** Samples land close to SRTT, RTTVAR shrinks, and the timeout settles just above the typical round trip.
- **A jittery path.** Even with the same average, samples that swing widely keep RTTVAR large. Fast samples count as surprises just as slow ones do, because the deviation ignores its sign. The timeout grows by four times that variation, so it does not fire on every delay spike.
- **A path that suddenly slows.** A run of longer samples raises SRTT slowly (an eighth at a time) but raises RTTVAR faster, so the margin widens before the average catches up.

For a concrete feel: a first sample of 100 ms gives a timeout of 300 ms (100 ms plus four times 50 ms). A second sample of 120 ms nudges the average up to 102.5 ms but shrinks the variation to 42.5 ms, so the timeout falls to 272.5 ms. These figures ignore the minimum-timeout floor covered in the next lesson.

## Key takeaways

- RFC 6298 smooths both RTT and the size of sample deviations.
- Update variation using the old smoothed RTT before updating the smoothed RTT itself.
- The raw estimator adds the larger of clock granularity and four variations; floors and timer policy apply separately.

## Further reading

- [RFC 6298: Computing TCP's Retransmission Timer](https://www.rfc-editor.org/rfc/rfc6298)
- [Congestion Avoidance and Control — Van Jacobson (1988)](https://ee.lbl.gov/papers/congavoid.pdf)
