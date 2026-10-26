---
id: nf-window-pipeline
sourceLesson: nf-error-control
title: Size a loss-free pipeline
level: advanced
minutes: 3
summary: Explain how a window covers feedback delay and why path changes alter the required flight allowance.
---

## Sliding windows

The fix is **pipelining**: permit several frames to be outstanding (sent but not yet acknowledged). Use a loss-free fixed-frame model with no queueing, processing, ACK transmission or framing gaps. This is the frame-based version of the earlier data-in-flight idea: feedback takes time, and a sender needs enough unacknowledged work to cover it.

A larger window lets the sender continue while acknowledgements are in transit. To keep sending continuously, the allowed frames must span the entire feedback cycle, including the first frame's transmission. Increasing the propagation RTT requires a larger window; increasing the link rate also requires more frames because each frame now takes less time to send.

```formula reference
N_fill = ⌈(L / R + RTT) / (L / R)⌉
where
N_fill: smallest whole-frame window that keeps this loss-free sender continuously busy
L: complete frame size in bits
R: link rate in bits per second
RTT: round-trip propagation time in seconds, excluding frame transmission, ACK transmission, processing and queueing
⌈ ⌉: ceiling, meaning round up to the next whole number
In words: allow enough frame transmissions to cover the time until the first acknowledgement returns; more frames cannot push utilisation above full link use.
```

Consider the preceding stop-and-wait example: a 1 Gbit/s link, 30 ms propagation round trip, and 1500-byte frames. Each frame takes 12 microseconds to transmit.

In this model the first acknowledgement returns 30.012 ms after sending starts. The sender can transmit 2,501 frames during that interval, so its window must allow that many to avoid becoming idle. Real framing, ACK transmission, processing, loss and queueing can change the required allowance.

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
