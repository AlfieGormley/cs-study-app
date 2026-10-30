---
id: tcp-mathis-loss-model
sourceLesson: tcp-performance
title: The Mathis model and its limits
level: advanced
minutes: 4
summary: The Mathis model: why a Reno-style flow's throughput falls with RTT and with the square root of the loss rate.
---

## Long transfers are loss-bound: the Mathis formula

The Mathis model approximates a sustained Reno-style congestion-avoidance flow with light/moderate loss, sufficient sender data and receive window, and no retransmission timeouts. It answers a practical question: how much throughput can a given loss rate allow on a given path? The ideal periodic-loss sawtooth, with one ACK per segment, yields:

```formula essential
X ≈ (MSS / RTT) × (C / √p)
where
X: the estimated throughput, in bytes per second (multiply by 8 for bits per second)
MSS: maximum segment size, the payload bytes per segment, for example 1,460 bytes
RTT: round-trip time, in seconds
C: a constant from the sawtooth shape, about 1.22 (the square root of 3/2) for one ACK per segment and periodic loss
p: the loss rate: the fraction of packets lost, for example 0.0001 for one in ten thousand
√: square root: the number that, multiplied by itself, gives the value inside; √0.0001 = 0.01
≈: approximately equal to
In words: throughput is about one segment per round trip, scaled up by 1.22 divided by the square root of the loss rate.
```

Where does the square root come from? The sawtooth. With one loss in every 1/p packets, the window climbs from half its peak back to its peak at one segment per round trip. Both the number of round trips in a cycle and the average window are proportional to the peak, so the packets sent per cycle grow with the **square** of the peak. Rarer losses therefore let the window climb higher, but only with one over the square root of the loss rate. The [Mathis et al. paper](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf) gives the full derivation.

For a sense of scale, with 1,460-byte segments and a 100 ms RTT the formula returns about **14 Mbit/s** at a 0.01% loss rate and about **1.4 Mbit/s** at 1%. These are model outputs, not universal caps or predictions for arbitrary packet-loss patterns. ACK behaviour and loss patterns change the constant; timeouts and other limits can invalidate the approximation. Notice that the link's capacity does not appear at all. Within the model:

- **Throughput is inversely proportional to RTT.** Doubling RTT halves the estimate when all other parameters stay fixed. Geographic distance does not by itself determine RTT.
- **Throughput falls with the square root of loss.** To double throughput you need **four times** less loss; quadrupling the loss rate halves it.
- **Long fat pipes need tiny loss rates**, which is why CUBIC and BBR exist. This Reno model is not a general throughput law for CUBIC or BBR.

Use the formula as a teaching comparison, not a unique diagnosis. Matching it does not rule out other bottlenecks. `ss -ti` exposes TCP state and counters on Linux; its retransmission counters are not automatically the model’s loss probability. Compare captures, application demand, receive windows, congestion-control state and link utilisation.

## Key takeaways

- The Mathis approximation describes a qualified Reno-style loss/RTT model without retransmission timeouts.
- Its square-root dependence follows from the ideal sawtooth packet count.
- The formula is a comparison tool rather than a universal TCP ceiling or a unique bottleneck diagnosis.

## Further reading

- [The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm — Mathis et al.](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Mathis and Mahdavi: Deprecating the TCP Macroscopic Model (2019 editorial)](https://ccronline.sigcomm.org/wp-content/uploads/2019/10/acmdl19-323.pdf)
