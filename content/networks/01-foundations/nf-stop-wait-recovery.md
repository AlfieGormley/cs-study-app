---
id: nf-stop-wait-recovery
sourceLesson: nf-error-control
title: FEC, ARQ and stop-and-wait
level: advanced
minutes: 4
summary: Compare repair with retransmission and calculate the cost of waiting for each acknowledgement.
---

## Recovering: FEC or ARQ?

| | FEC | ARQ |
|---|---|---|
| How | Extra bits fix errors | Resend what was lost |
| Cost | Redundancy and coding work | ACK/state overhead plus retransmissions |
| Latency | Encoding/decoding and possible buffering delay | Loss detection, retransmission and propagation delay |
| Design considerations | Can reduce retries; code and channel determine effectiveness | Feedback delay, loss and retransmission cost matter |

Real systems can combine FEC with retransmission. FEC is not absent from Ethernet: several PHYs use it, including Reed–Solomon coding in high-speed variants. Ordinary Ethernet MAC handling discards invalid-FCS frames without a MAC-level request to resend them; a higher layer may recover, depending on the protocol. FEC can avoid a retransmission round trip, but adds coding work and cannot correct arbitrary damage.

> [!note] Content omitted after review
> Universal bit-error rates and blanket claims about coding or retransmission across all wireless and deep-space links are omitted. Those require a specific standard, mode, mission or measurement that this lesson has not established.

## Stop-and-wait

The simplest ARQ: send one frame, wait for its ACK, then send the next. If no ACK arrives before a timeout, resend. A 1-bit sequence number (alternating 0 and 1) lets the receiver spot a duplicate when the frame arrived but the ACK was lost.

Assume ordered channels, detectable corruption, no arbitrarily delayed duplicates surviving sequence-number reuse, and retry behaviour that eventually permits delivery. For the loss-free timing model, ignore ACK transmission, processing, queueing and framing gaps. Each cycle the sender spends one frame time transmitting, then a round trip waiting for the ACK. Its **utilisation** is the fraction of time it is actually sending:

```formula
U = (L / R) / (L / R + RTT)
where
U: the sender's utilisation: the fraction of time the link is busy sending data, from 0 to 1
L: the complete frame size, in bits
R: the data-link rate, in bits per second
L / R: the frame's transmission time, in seconds
RTT: the round-trip propagation delay, in seconds, excluding the data frame's own transmission time
In words: the sender is busy for one frame time out of every frame time plus round trip; when the round trip is much longer than the frame time, the link sits almost idle.
```

> [!example] Stop-and-wait across a country
> 1 Gbit/s, 30 ms RTT, 1500-byte frames (12,000 bits). The utilisation comes out at about **0.04%**, so throughput is only about **400 kbit/s** on a gigabit link.

```formula
L / R = 12,000 bit / (10⁹ bit/s) = 12 µs
U = 0.012 ms / (0.012 ms + 30 ms)
U = 0.012 / 30.012 ≈ 0.0004 = 0.04%
X = L / (L / R + RTT)
X = 12,000 bit / 30.012 ms ≈ 400 kbit/s
where
L: the frame size, 12,000 bits
R: the link rate, 1 Gbit/s = 10⁹ bits per second
bit: one binary digit; bit/s is bits per second
s: seconds
µs: microseconds; 12 µs = 0.012 ms
ms: milliseconds, thousandths of a second
U: the utilisation
RTT: the round-trip propagation delay, 30 ms
X: the throughput: one frame delivered per cycle
kbit/s: kilobits per second; 1 kbit is 1,000 bits
≈: approximately equal to
In words: the sender transmits for 12 µs and then waits 30 ms, so the gigabit link is busy only 0.04% of the time and carries about 400 kbit/s.
```

## Key takeaways
- FEC and ARQ can be combined; ordinary Ethernet MAC handling does not request every damaged frame again.
- Stop-and-wait wastes capacity when one frame time is short beside the feedback round trip.

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
