---
id: nf-queue-utilisation
sourceLesson: nf-performance
title: Why busy queues become slow
level: basic
minutes: 4
summary: Use the stated M/M/1 assumptions to relate utilisation to waiting time and bufferbloat.
---

## Why queues explode near full load

The question here is "how busy is this link, and how long will packets wait?" The **traffic intensity** compares the bits arriving each second with the bits the link can send each second:

```formula
ρ = (La) / R
where
ρ: rho, the traffic intensity (also called utilisation or load): the fraction of the link's capacity being asked for; it has no unit
L: the mean packet length, in bits
a: the average packet arrival rate, in packets per second
R: the link's transmission rate, in bits per second
In words: bits arriving per second divided by bits the link can send per second. At ρ = 1 traffic arrives exactly as fast as the link can send it; above 1 it arrives faster.
```

For example, 7,500 packets per second of 1500-byte packets on a 100 Mbit/s link:

```formula
ρ = 12,000 bit × 7,500 /s / (10⁸ bit/s)
ρ = 9 × 10⁷ / 10⁸ = 0.9
where
ρ: rho, the traffic intensity (no unit)
bit: one binary digit; each 1500-byte packet is 12,000 bits
s: seconds; /s means "per second"
In words: the traffic asks for 90 Mbit/s of a 100 Mbit/s link, a load of 0.9 (90%).
```

With sustained offered load above service capacity, an ideal infinite queue has no stable finite backlog; a finite buffer instead reaches capacity and drops or otherwise rejects excess traffic. More surprisingly, the queue is already long well *before* ρ reaches 1.

Queueing theory's simplest model, the **M/M/1 queue**, shows why. It assumes Poisson arrivals (packets arrive independently at random, at a steady average rate), independent exponential service times (packet transmission times vary randomly around their mean), one server (one output link), infinite waiting space and ρ < 1. Its mean wait in the queue is:

```formula
W_q = (ρ / (1 − ρ)) T_s
where
W_q: the mean time a packet waits in the queue before its own transmission starts, in seconds
ρ: rho, the traffic intensity, between 0 and 1; the formula only holds for ρ < 1
T_s: the mean service time: the average time the link takes to transmit one packet, in seconds
In words: the wait, measured in packet times, is ρ / (1 − ρ). The bottom of the fraction shrinks towards zero as the load approaches 100%, so the wait shoots up.
```

At 90% load, for example:

```formula
W_q = 0.9 / (1 − 0.9) × T_s
W_q = 0.9 / 0.1 × T_s = 9 × T_s
where
W_q: the mean queueing wait
T_s: the mean service time (one packet time)
In words: at 90% load an average packet waits as long as it takes to send 9 packets before it even starts transmitting.
```

Fixed-size packets have deterministic rather than exponential transmission times, so this table is an illustrative queue model:

| Utilisation ρ | Average wait (packet times) |
|---|---|
| 50% | 1 |
| 80% | 4 |
| 90% | 9 |
| 99% | 99 |

Real traffic, packet lengths and scheduling differ; this model is neither a universal prediction nor a bound. This is why network engineers treat links running near 100% as a problem, and why a link at 95% "average" utilisation can feel terrible.

A related failure is **bufferbloat**: routers and home modems with very large buffers let queues grow to hundreds of milliseconds rather than dropping packets early. Throughput looks fine but latency becomes awful, ruining video calls and games while a large upload runs. Active queue management (CoDel, FQ-CoDel) addresses this.

## Key takeaways
- The M/M/1 mean wait grows nonlinearly as load approaches capacity.
- Its random-service, infinite-buffer assumptions do not describe every real router.

## Further reading
- [Primer on Latency and Bandwidth — High Performance Browser Networking](https://hpbn.co/primer-on-latency-and-bandwidth/)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)
- [Network delay — Wikipedia](https://en.wikipedia.org/wiki/Network_delay)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Bufferbloat — Wikipedia](https://en.wikipedia.org/wiki/Bufferbloat)
- [Goodput — Wikipedia](https://en.wikipedia.org/wiki/Goodput)

- [RFC 8290: FQ-CoDel](https://www.rfc-editor.org/rfc/rfc8290)
- [RFC 8446: TLS 1.3 and early-data replay considerations](https://www.rfc-editor.org/rfc/rfc8446)
- [MIT queueing lecture: M/M/1 assumptions](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-spring-2006/1a538356bf7a1f78408de525dd2d1032_lec21.pdf)
