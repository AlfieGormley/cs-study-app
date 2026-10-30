---
id: wm-debug-throughput-models
title: Loss-limited and window-limited TCP models
level: advanced
minutes: 4
summary: The periodic-loss Reno model has explicit assumptions and does not describe every congestion control.
sourceLesson: wm-debugging
---

A single TCP connection can be far slower than the link it runs over. Two simple models predict why: one says loss and distance limit throughput, the other says the window of data in flight does. Knowing which applies tells you what to fix.

## Loss-limited throughput

Loss-based TCP grows its congestion window by about one segment per round trip and roughly halves it at each loss. Two things follow. A longer round trip means slower growth, and more frequent loss means the window is cut before it gets large. The simplified **Mathis model** for Reno congestion avoidance captures both:

```formula essential
X ≈ (MSS / RTT)(1.22 / √(p))
where
X: the model's long-run throughput for one TCP flow, in bits per second (bit/s)
MSS: maximum segment size: the most payload in one TCP segment, in bits for this formula (1,460 bytes is 11,680 bits)
RTT: the round-trip time, in seconds (s)
p: the packet loss probability as a fraction, e.g. 0.0001 for one packet in 10,000
√: square root
1.22: approximately the square root of 3/2, which comes from the saw-tooth shape of Reno's window
≈: approximately equal to
In words: throughput is one segment per round trip, multiplied by a factor that grows as loss gets rarer; doubling the RTT halves throughput, while cutting loss by 100 times only raises it 10 times.
```

What it predicts:

- **Distance hurts directly.** The same 0.01% loss gives about 14 Mbit/s at 100 ms RTT but about 140 Mbit/s at 10 ms. A transfer that is fine within a city can crawl across an ocean with exactly the same loss rate.
- **Loss hurts by its square root.** Halving the loss rate raises throughput by only about 40%. Tiny loss rates, invisible to a short ping test, can still cap a long-distance flow.
- **A single flow can be far below link capacity** even when nothing is "wrong" with the link.

The model assumes periodic loss, one ACK per segment, enough data and window, light-to-moderate loss and no timeout-dominated behaviour. It describes classic Reno; CUBIC and especially BBR respond to loss differently, so treat it as an explanation of the trend, not a prediction for every stack. Parallel streams can hide per-flow limits, so compare single- and multi-stream tests with endpoint measurements.

## Window-limited throughput

Without loss, a single flow is capped at **one window per round trip**: the sender can have at most one window of unacknowledged data in flight, and must wait about a round trip for acknowledgments before sending more. To fill a link, the window must be at least the link rate times the RTT, the **bandwidth-delay product** (BDP).

```formula reference
X_max = (8W) / RTT
where
X_max: the window-limited throughput, in bits per second (bit/s)
W: the effective window: the unacknowledged data allowed in flight, in bytes (B)
RTT: the round-trip time, in seconds (s)
B: byte, 8 bits; multiplying by 8 converts bytes to bits
In words: a flow can send at most one window per round trip, so its throughput limit is the window divided by the round-trip time, whatever the link speed.
```

For example, filling 1 Gbit/s at 100 ms RTT needs 12.5 MB in flight, while a flow limited to a 4 MB window at that RTT tops out around 320 Mbit/s even on a 10 Gbit/s link. The effective window is the smaller of the congestion window and the receiver's advertised window; socket-memory limits influence both but are not identical to either. If a long-distance flow is window-limited, upgrading the link does nothing, while raising the window limits (for example receive-buffer autotuning limits) does.

> [!note] Evidence limits
> Fixed SYN retry schedules, universal timeout advice and diagnoses inferred from one counter or trace are intentionally omitted. Sample outputs are illustrative. Real-device captures, WAN impairments and production incident causes were not measured in this review.

## Key takeaways
- The periodic-loss Reno model has explicit assumptions and does not describe every congestion control.
- An effective flight window divided by RTT is a per-flow limit, so long paths need large windows to fill fast links.

## Further reading
- [Mathis et al.: The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Linux TCP configuration: windows, timeouts and recovery](https://docs.kernel.org/networking/ip-sysctl.html)
