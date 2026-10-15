---
id: tcp-bufferbloat-aqm
sourceLesson: tcp-performance
title: Queueing delay, bufferbloat and AQM
level: advanced
minutes: 4
summary: Queueing delay, bufferbloat and AQM, with worked examples and explicit assumptions.
---

## Bufferbloat

Routers need buffers to absorb bursts. The traditional rule of thumb was one BDP of buffering per link. But memory became cheap, and many home routers, cable modems and mobile base stations were built with **far** more.

A saturated loss-based flow with a large tail-drop queue can sustain substantial queue occupancy. ECN, AQM, competing traffic and sender limits change this behaviour. For a packet joining a FIFO, the wait is the backlog ahead of it divided by the rate at which the link drains it. For example, 256 KiB queued at a 2 Mbit/s uplink:

```formula
T_q = Q × 8 / R
T_q = 256 × 1,024 × 8 bit / (2 × 10^6 bit/s)
T_q ≈ 1.05 s
where
T_q: queueing delay, how long the new packet waits before its own transmission starts, in seconds (s)
Q: the backlog ahead of it, in bytes; 256 KiB = 256 × 1,024 = 262,144 bytes
R: the link rate, in bits per second (bit/s); 2 Mbit/s = 2 × 10^6 bit/s
bit: binary digit; × 8 turns bytes into bits
s: seconds
≈: approximately equal to
In words: about 2.1 million bits queued in front of you on a 2 million-bit-per-second link means about a second of waiting.
```

A packet behind that backlog waits about 1.05 seconds before its own transmission, ignoring overhead and changes in link rate. Other queues or priority classes can see different delays. Sustained excessive queueing is **bufferbloat**: high throughput can coexist with poor latency under load. The following RTTs are illustrative, adding that queue to a 20 ms idle path:

```formula
RTT_load ≈ RTT_idle + T_q
RTT_load ≈ 20 ms + 1,050 ms = 1,070 ms
where
RTT_load: the round-trip time while the upload fills the queue, in milliseconds (ms)
RTT_idle: the round-trip time with empty queues, here 20 ms
T_q: the queueing delay from the full buffer, about 1,050 ms
ms: milliseconds
≈: approximately equal to
In words: a full upstream buffer turns a 20 ms path into a one-second path for every packet that has to wait behind it.
```

## Active queue management

Active queue management signals congestion before excessive persistent queues develop. Delay is the signal used by CoDel; other AQM designs use other measurements:

- **CoDel** (Controlled Delay, [RFC 8289](https://www.rfc-editor.org/rfc/rfc8289)) tracks how long packets wait. Its usual target and interval are 5 ms and 100 ms. Persistent excess sojourn time can trigger drops or ECN marks; a remaining-backlog check avoids needlessly starving the link. The target is not a guaranteed maximum for every packet’s delay, and finite buffers can still drop bursts.
- **fq_codel** ([RFC 8290](https://www.rfc-editor.org/rfc/rfc8290)) adds **flow queueing**: packets are hashed into queues, with modified deficit round-robin scheduling and CoDel. This reduces interference between bulk and sparse traffic; hash collisions and shared bottlenecks mean isolation is not absolute.
- **L4S** ([RFC 9330](https://www.rfc-editor.org/rfc/rfc9330)) describes an architecture using scalable congestion control and compatible ECN/AQM behaviour to target low queueing delay. It is not merely a replacement name for CoDel or a guarantee of one-millisecond end-to-end latency.

**Pacing** spreads transmissions and can reduce bursts; **BBR** uses a path model but can still build queues. Locate the actual bottleneck. When it is an inaccessible modem/ISP queue, suitable shaping on a controlled router can move the bottleneck to a queue where AQM is effective; measure the throughput trade-off.

## Key takeaways

- FIFO backlog divided by service rate estimates waiting time before transmission under fixed-rate assumptions.
- Persistent excess queueing can coexist with high throughput and harm latency.
- CoDel, flow queueing, pacing and shaping address related but distinct causes of delay.

## Further reading

- [The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm — Mathis et al.](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Introduction to bufferbloat — bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Introduction/)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The QUIC Transport Protocol: Design and Internet-Scale Deployment — Google (SIGCOMM 2017)](https://research.google/pubs/the-quic-transport-protocol-design-and-internet-scale-deployment/)
- [RFC 7413: TCP Fast Open](https://www.rfc-editor.org/rfc/rfc7413)
- [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 9002: QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002)
- [Mathis and Mahdavi: Deprecating the TCP Macroscopic Model (2019 editorial)](https://ccronline.sigcomm.org/wp-content/uploads/2019/10/acmdl19-323.pdf)
