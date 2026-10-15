---
id: nf-error-probability
sourceLesson: nf-error-control
title: Frame errors and retransmission work
level: advanced
minutes: 4
summary: Calculate independent-bit damage probability and qualified ideal retransmission efficiency.
---

### When errors happen: the maths

Two questions: how likely is a frame to be damaged, and how many tries does it then take on average? If attempts independently fail with the same probability and retries continue until success, the number of attempts follows the geometric distribution:

```formula
E[A] = 1 / (1 − p)
where
E[A]: the expected (average) number of attempts needed to deliver one frame
p: the probability that any one attempt fails, between 0 and 1 (must be below 1)
In words: if a fraction p of attempts fail, then on average 1 / (1 − p) attempts are needed per success; at p = 0.5, two attempts.
```

This counts attempts, not elapsed time: timeout and ACK behaviour still matter.

If individual bits flip independently, a frame survives only if every one of its bits survives:

```formula
p = 1 − (1 − b)^n
p ≈ nb
where
p: the probability that an n-bit frame has at least one flipped bit
b: the probability that any single bit flips (the bit error rate)
n: the number of bits in the frame
≈: approximately equal to
In words: each bit survives with probability 1 − b, so all n survive with probability (1 − b)^n; one minus that is the chance something flipped. When n × b is small (well below 1) this is close to n × b.
```

Treating this as frame-loss probability additionally assumes every such frame is rejected; FEC and undetected errors change that mapping.

For a hypothetical uncoded 12,000-bit frame at a bit error rate of 10⁻⁶ (one bit in a million):

```formula
p = 1 − (1 − 10⁻⁶)^12000
p ≈ 0.011928 = 1.1928%
E[A] = 1 / (1 − 0.011928) ≈ 1.0121
1 − p ≈ 0.988072 = 98.8072%
where
p: the probability that a 12,000-bit frame is damaged
E[A]: the expected number of attempts per delivered frame
≈: approximately equal to
In words: about 1.2% of frames are damaged, so on average a frame needs about 1.012 attempts, and about 98.8% of transmission time goes on attempts that succeed.
```

So about **1.19%** of frames are damaged and a frame needs about **1.0121** attempts under the independent retry model. A continuously busy sender retransmitting only failed frames spends about **98.81%** of frame transmission time on successful attempts. This is an ideal efficiency, not a finite-window throughput prediction.

Go-Back-N also retransmits later outstanding frames discarded after a gap. Its actual goodput depends on timer values, acknowledgements, propagation, window size and the loss process.

MIT's lecture gives an **approximate** Go-Back-N model: choose N to fill the loss-free feedback cycle, set the timeout to N frame times, ignore ACK errors, and charge N transmissions for each failed delivery attempt:

```formula
T_avg = 1 + (Np) / (1 − p)
η = 1 / T_avg
η = (1 − p) / (1 + (N − 1)p)
where
T_avg: the expected number of frame transmissions per delivered frame
N: the window size in frames (here also the number of frames resent after each failure)
p: the probability that a frame transmission fails
η: eta, the efficiency: the fraction of transmissions that deliver new frames
In words: each failure costs a whole window of N retransmissions, so with a big window even a small failure rate wastes most of the link.
```

With the example's numbers:

```formula
η = 0.9880717 / (1 + 2,500 × 0.0119283)
η ≈ 0.98807 / 30.82 ≈ 0.0321 = 3.21%
where
η: eta, the Go-Back-N efficiency for N = 2,501 and p ≈ 0.0119283
≈: approximately equal to
In words: with a 2,501-frame window and 1.2% damaged frames, only about **3.21%** of transmissions deliver new data in this model.
```

It is a model of retransmission work, not a universal finite-window or measured-network prediction.

> [!note] Content omitted after review
> Measured protocol-performance comparisons are absent because no link implementation or workload has been benchmarked here. The formulas describe their stated idealised models.

## Key takeaways
- Independent bit and attempt assumptions produce geometric retry averages.
- The approximate Go-Back-N work model is not a measured or universal finite-window goodput prediction.

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
