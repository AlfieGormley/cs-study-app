---
id: nf-error-probability
sourceLesson: nf-error-control
title: Frame errors and retransmission work
level: advanced
minutes: 3
summary: Explain how frame size, bit errors, coding and recovery strategy affect retransmission work.
---

A reliability design needs to distinguish damaged bits, rejected frames and failed delivery attempts. These are related, but not interchangeable measurements.

## Larger frames expose more bits

Under an **independent-bit error model**, each bit has the same independent chance of flipping. A frame is damaged if any of its bits flips. A longer frame exposes more bits, so it is more likely to contain damage at the same bit-error probability.

For a hypothetical uncoded 12,000-bit frame with one-in-a-million independent bit-error probability, about 1.2% of frames contain at least one flipped bit. This is a modelled result; burst errors do not satisfy the independence assumption.

```formula reference
p = 1 − (1 − b)^n
where
p: probability that the frame contains at least one flipped bit, a unitless fraction from zero to one
b: independent bit-flip probability, the same for each bit and between zero and one
n: number of bits in the frame, a positive whole number
In words: a frame is undamaged only when every bit survives, so larger frames are more likely to contain damage under the stated independent-bit model.
```

Treating damage probability as frame-loss probability additionally assumes every damaged frame is rejected. Forward error correction can repair damage; an integrity check can also miss some errors. Raw errors before coding do not establish residual loss after coding.

## Retries consume capacity and time

If each attempt fails independently with the same probability below one, and retries continue until success, the average attempt count follows a geometric model.

```formula reference
E[A] = 1 / (1 − p)
where
E[A]: expected number of attempts needed per successful delivery, counting the original attempt and any retries
p: independent failure probability of each complete attempt, a unitless fraction from zero up to but excluding one
In words: higher attempt-failure probability requires more attempts per success on average; when half of attempts fail, the average is two attempts per success.
```

For the hypothetical frame-damage example, if every damaged frame causes an independent retry failure, delivery needs about 1.012 attempts on average. That counts work, not elapsed time: timeouts, acknowledgements and feedback delay still matter.

## Recovery strategy changes the cost

Selective Repeat can retain and acknowledge later frames after a gap, resending only those still unacknowledged. Go-Back-N discards later out-of-order frames in its textbook model, so one missing frame can force additional retransmissions.

The difference can be especially costly on long paths with large windows. Its size depends on residual losses, timers, acknowledgements, memory and processing; no single loss-percentage formula predicts every implementation's goodput.

Larger frames spread fixed headers over more data, but increase exposure to independent bit errors. Suitable FEC can reduce residual loss without waiting a round trip, at the cost of redundancy and decoding work. Choose a frame size and recovery design using the actual channel and workload.

## Key takeaways
- Longer frames have more opportunities for damage under independent bit errors.
- Raw bit errors, residual frame loss, retry work and elapsed delivery time are different quantities.
- FEC and selective recovery trade overhead and memory against retransmission cost.

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
