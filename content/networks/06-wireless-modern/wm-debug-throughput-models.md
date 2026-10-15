---
id: wm-debug-throughput-models
title: Loss-limited and window-limited TCP models
level: advanced
minutes: 4
summary: The periodic-loss Reno model has explicit assumptions and does not describe every congestion control.
sourceLesson: wm-debugging
---

This unit focuses on loss-limited and window-limited TCP models. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Loss-limited throughput

TCP throughput falls sharply with loss, especially over long RTTs. The simplified Reno congestion-avoidance Mathis model below assumes periodic loss, one ACK per segment, adequate data/window, light/moderate loss and no RTO-dominated behaviour. Its constant 1.22 is approximately the square root of 3/2, which falls out of the saw-tooth shape of Reno's congestion window: it grows by one segment per round trip and halves at each loss.

```formula
X ≈ (MSS / RTT)(1.22 / √(p))
MSS / RTT = (1460 × 8 bit) / 0.1 s
MSS / RTT = 116,800 bit/s
X ≈ (116,800 bit/s × 1.22) / √(0.0001)
X ≈ (116,800 bit/s × 1.22) / 0.01
X ≈ 14,249,600 bit/s ≈ 14.2 Mbit/s
where
X: the model's long-run throughput for one TCP flow, in bits per second (bit/s)
MSS: maximum segment size: the most payload in one TCP segment, 1,460 bytes here (× 8 to convert to bits)
RTT: the round-trip time, 100 ms = 0.1 seconds (s)
p: the packet loss probability as a fraction: 0.0001 is 0.01%, one packet in 10,000
√: square root; √(0.0001) = 0.01
bit: one binary digit
bit/s: bits per second
Mbit/s: megabits per second, one million bits per second
s: second
≈: approximately equal to
In words: throughput is one segment per round trip, multiplied by a factor that grows as loss gets rarer; halving RTT doubles it, but cutting loss by 100 times only multiplies it by 10.
```

The supplied Reno model returns about 14.2 Mbit/s; it is not a general law for CUBIC or BBR, nor a ceiling established by a ping loss estimate. Low loss can be missed in short samples. Parallel streams can also hide per-flow limits, so compare single- and multi-stream tests with endpoint resource measurements.

## Window-limited throughput

Without loss, a single flow is capped at **one window per round trip**: the sender can have at most one window of unacknowledged data in flight per round trip. To fill 1 Gbit/s at 100 ms RTT, TCP needs a window equal to the bandwidth-delay product:

```formula
X_max = (8W) / RTT
BDP = (R RTT) / 8
BDP = (10^9 bit/s × 0.1 s) / 8
BDP = 12,500,000 B = 12.5 MB
where
X_max: the window-limited throughput, in bits per second (bit/s)
W: the effective window: the unacknowledged data allowed in flight, in bytes (B)
RTT: the round-trip time, in seconds (s); 0.1 s here
BDP: the bandwidth-delay product: the data that must be in flight to keep the link full, in bytes
R: the link rate to fill, 1 Gbit/s = 10^9 bit/s here
bit/s: bits per second
B: byte, 8 bits; multiplying or dividing by 8 converts between bytes and bits
MB: megabyte, 10^6 bytes
s: second
In words: a full pipe holds rate × round-trip time of data, so a 1 Gbit/s, 100 ms path needs 12.5 MB in flight.
```

If the measured effective flight window is 4,000,000 bytes at a fixed 100 ms RTT, the simple limit is 8 × 4,000,000 bits ÷ 0.1 s = 320 Mbit/s. Socket-memory limits are not identical to that window; other bottlenecks can reduce achieved throughput.

> [!note] Evidence limits
> Fixed SYN retry schedules, universal timeout advice and diagnoses inferred from one counter or trace are intentionally omitted. Sample outputs are illustrative. Real-device captures, WAN impairments and production incident causes were not measured in this review.

## Key takeaways
- The periodic-loss Reno model has explicit assumptions and does not describe every congestion control.
- An effective flight window divided by RTT is a conditional per-flow limit, distinct from socket-memory sizes.

## Further reading
- [Mathis et al.: The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Linux TCP configuration: windows, timeouts and recovery](https://docs.kernel.org/networking/ip-sysctl.html)
