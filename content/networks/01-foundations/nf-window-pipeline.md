---
id: nf-window-pipeline
sourceLesson: nf-error-control
title: Size a loss-free pipeline
level: advanced
minutes: 3
summary: Calculate how many outstanding frames cover a full feedback cycle.
---

## Sliding windows

The fix is **pipelining**: permit several frames to be outstanding (sent but not yet acknowledged). Use a loss-free fixed-frame model with no queueing, processing, ACK transmission or framing gaps. The formula defines the window size below. To keep the link busy the window must cover a full round trip, which is the bandwidth-delay product from the delay and bandwidth-delay-product units:

```formula
U = min(1, N(L / R) / (L / R + RTT))
N_fill = ⌈(L / R + RTT) / (L / R)⌉
where
U: the sender's utilisation, from 0 to 1
min: the minimum, the smaller of the two values; utilisation cannot exceed 1 (100%)
N: the window: how many frames may be outstanding at once
L / R: one frame's transmission time: frame size L in bits divided by link rate R in bits per second
RTT: the round-trip propagation delay, in seconds
N_fill: the smallest window that keeps the link continuously busy
⌈ ⌉: the ceiling function: round up to the next whole number
In words: N frames keep the sender busy N times longer per cycle; once the window covers a whole cycle (one frame time plus a round trip), the link never idles.
```

Consider the preceding stop-and-wait example: a 1 Gbit/s link, 30 ms propagation round trip, and 1500-byte frames. Each frame takes 12 microseconds to transmit:

```formula
N_fill = ⌈(0.012 ms + 30 ms) / 0.012 ms⌉
N_fill = ⌈30.012 / 0.012⌉ = 2,501
where
N_fill: the window, in frames, that fills the 1 Gbit/s, 30 ms path
ms: milliseconds; 0.012 ms (12 µs) is one 12,000-bit frame time at 1 Gbit/s
⌈ ⌉: the ceiling function: round up to a whole number of frames
In words: the first ACK returns 30.012 ms after the first frame starts, enough time to send **2,501 frames**, so that many must be allowed in flight.
```

The next unit compares two strategies for handling a loss inside that window.

## Key takeaways
- A continuously busy sender needs enough outstanding frames for the whole loss-free feedback cycle.
- This model excludes ACK transmission, queueing, processing and framing gaps.

## Further reading
- [Cyclic redundancy check — Wikipedia](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
- [RFC 1071: Computing the Internet Checksum](https://www.rfc-editor.org/rfc/rfc1071)
- [Koopman: Best CRC polynomials](https://users.ece.cmu.edu/~koopman/crc/)
- [Sliding window protocol — Wikipedia](https://en.wikipedia.org/wiki/Sliding_window_protocol)
- [Selective Repeat ARQ — Wikipedia](https://en.wikipedia.org/wiki/Selective_Repeat_ARQ)
- [End-to-end principle — Wikipedia](https://en.wikipedia.org/wiki/End-to-end_principle)

- [Koopman: CRC-32 distance table](https://users.ece.cmu.edu/~koopman/crc/crc32.html)
- [Stone and Partridge: When the CRC and TCP Checksum Disagree](https://conferences.sigcomm.org/sigcomm/2000/conf/paper/sigcomm2000-9-1.pdf)
- [RFC 3366: Advice to Link Designers on Link ARQ](https://www.rfc-editor.org/rfc/rfc3366.html)
- [MIT: ARQ protocols](https://ocw.mit.edu/courses/16-36-communication-systems-engineering-spring-2009/resources/mit16_36s09_lec18/)
