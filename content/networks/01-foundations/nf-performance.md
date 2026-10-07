---
id: nf-performance
title: Bandwidth, latency and throughput
level: basic
minutes: 13
summary: The four components of delay and how to calculate each, why queues explode near full load, the bandwidth-delay product, and why throughput and goodput are lower than the link speed.
---

Two words get used loosely in everyday talk about networks: "fast" and "slow". A "fast" connection might mean one that moves a lot of data per second, or one that responds quickly. These are different properties, and confusing them leads to bad decisions, such as paying for more bandwidth when the real problem is latency.

This lesson gives you the vocabulary and the arithmetic. You will use it in every later lesson, especially when we reach TCP.

## Bandwidth and latency

- **Bandwidth** (or link rate, capacity) is how many bits per second a link can push onto the wire. Think of the *width* of a pipe.
- **Latency** (delay) is how long it takes one bit, or one packet, to get from one end to the other. Think of the *length* of the pipe.

A motorway analogy: bandwidth is the number of lanes, latency is how long the drive takes. Adding capacity does not shorten the physical route, but it can reduce congestion delays. Likewise, greater link rate can reduce transmission and queueing delay without changing propagation speed.

> [!warning] Units
> Network rates use decimal SI units and **bits**: 1 Mbit/s is 1,000,000 bits per second. File sizes are usually in **bytes**, sometimes binary (1 KiB = 1024 bytes). A "100 Mbit/s" connection downloads at most 12.5 MB/s. Mixing bits and bytes is the most common calculation mistake, so write the units down.

## The four components of delay

When a packet crosses one hop (a link plus the device at the far end), its delay has four parts.

```
 queue    transmit     propagate
[ | | ]-> [=====]  ~~~~~~~~~~~~~~> router
 d_queue   d_trans      d_prop      d_proc
```

### 1. Transmission delay

The time to push all the packet's bits onto the link:

`d_trans = L / R`

where L is the number of bits counted at the modelled layer and R is the corresponding rate. The table ignores additional framing and encoding overhead.

A 1500-byte packet is 12,000 bits:

| Link rate | d_trans |
|---|---|
| 10 Mbit/s | 1.2 ms |
| 100 Mbit/s | 120 µs |
| 1 Gbit/s | 12 µs |
| 10 Gbit/s | 1.2 µs |

### 2. Propagation delay

The time for a bit to travel the length of the medium:

`d_prop = d / s`

where d is distance and s the signal speed. For a common teaching approximation to solid-glass fibre and some cables, s is roughly 2 × 10⁸ m/s, about two-thirds of the speed of light (lesson 3 explains why). A handy rule: **about 5 µs per kilometre**, or 1 ms per 200 km.

Transmission and propagation are often confused. Transmission depends on the packet size and the link rate, and has nothing to do with distance. In this model, propagation depends on path length and signal speed, not packet size or bit rate. An upgrade that changes the medium, wavelength or route can also change propagation; increasing the rate alone does not.

> [!example] A hypothetical 5,600 km fibre route
> Assume 200,000 km/s propagation in both directions. One-way propagation is 5,600 / 200,000 s = 28 ms, so the propagation contribution to RTT is 56 ms. Longer routes and equipment add delay. This is a specified model, not a measured or universal city-pair RTT; such measured figures are omitted without a route and measurement source.

### 3. Queueing delay

If packets arrive at a router faster than its output link can send them, they wait in a buffer. Queueing delay can be zero on an idle link and hundreds of milliseconds on a congested one. Variation in packet delay is commonly called **jitter**; queueing is one contributor, not the only possible source.

### 4. Processing delay

The time for a device to examine the header, look up where to send the packet and check for errors. The value depends on the hardware, software, configured processing and load; no universal per-router timing is established here.

### Putting it together

The delay for one hop is:

`d_hop = d_proc + d_queue + d_trans + d_prop`

The calculations below assume **store-and-forward**: a packet must arrive completely before it can be sent on, so the transmission delay is paid again on every link. Cut-through forwarding can overlap reception with onward transmission and needs a different model.

> [!example] Two-hop calculation
> Ignore framing overhead and assume store-and-forward. Host A sends a 1500-byte packet to host B through one router. Both links run at 100 Mbit/s; they are 200 km and 800 km long. The router takes 20 µs to process the packet and there is no queue.
> - Transmission: 2 links × 120 µs = 240 µs
> - Propagation: 1,000 km × 5 µs/km = 5,000 µs
> - Processing: 20 µs
> - Total ≈ **5.26 ms**, dominated by propagation.

The same arithmetic in Python:

```python
def hop_delay(bits, rate, km, proc=0.0,
              queue=0.0, speed=2e8):
    if (rate <= 0 or speed <= 0
            or min(bits, km, proc,
                   queue) < 0):
        raise ValueError("invalid delay")
    trans = bits / rate
    prop = km * 1000 / speed
    return proc + queue + trans + prop

bits = 1500 * 8
total = (hop_delay(bits, 100e6, 200)
         + hop_delay(bits, 100e6, 800,
                     proc=20e-6))
print(f"{total * 1e3:.2f} ms")  # 5.26 ms
```

## Why queues explode near full load

Let a be the average packet arrival rate (packets per second), and L the mean packet length in bits. The **traffic intensity** is:

`ρ = L × a / R`

the fraction of the link's capacity being asked for. With sustained offered load above service capacity, an ideal infinite queue has no stable finite backlog; a finite buffer instead reaches capacity and drops or otherwise rejects excess traffic. More surprisingly, the queue is already long well *before* ρ reaches 1.

For an M/M/1 queue with Poisson arrivals, independent exponential service times, one server, infinite waiting space and ρ < 1, mean queueing wait is ρ / (1 − ρ) times the **mean** service time. Fixed-size packets have deterministic rather than exponential transmission times, so this table is an illustrative queue model:

| Utilisation ρ | Average wait (packet times) |
|---|---|
| 50% | 1 |
| 80% | 4 |
| 90% | 9 |
| 99% | 99 |

Real traffic, packet lengths and scheduling differ; this model is neither a universal prediction nor a bound. This is why network engineers treat links running near 100% as a problem, and why a link at 95% "average" utilisation can feel terrible.

A related failure is **bufferbloat**: routers and home modems with very large buffers let queues grow to hundreds of milliseconds rather than dropping packets early. Throughput looks fine but latency becomes awful, ruining video calls and games while a large upload runs. Active queue management (CoDel, FQ-CoDel) addresses this.

## The bandwidth-delay product

For a steady window-limited flow, how much unacknowledged data corresponds to a target payload rate? Multiply that rate by its acknowledgement round-trip time, using consistent units:

`BDP = R × RTT`

For a hypothetical payload rate of 1 Gbit/s and a 70 ms RTT:

`1 × 10⁹ × 0.070 = 70 Mbit = 8.75 MB`

That is how much a sender must have sent but not yet had acknowledged to keep the pipe full. If the sender's window (the amount it may have unacknowledged) is smaller than the BDP, it sits idle waiting for acknowledgements, and throughput is capped at:

`throughput ≤ window / RTT`

> [!example] The original TCP window limit
> Without negotiated window scaling, TCP’s 16-bit advertised receive window cannot represent more than 65,535 bytes. This bounds steady new-data throughput when that window is the active constraint. Over a 70 ms RTT that caps throughput at 65,535 × 8 / 0.070 ≈ **7.5 Mbit/s**, no matter how fast the link is. The TCP **window scale** option (RFC 7323) allows larger receive windows when both endpoints negotiate it; support and configuration must be checked.

Paths with a large BDP are called **long fat networks**. They need large windows, large socket buffers and loss recovery that copes with many packets in flight. Lesson 6 and the TCP module build on this.

## Throughput and goodput

**Throughput** is the rate at which data actually gets through, as opposed to the link's nominal rate. End to end, it is limited by the slowest link on the path, the **bottleneck**:

`throughput ≤ min(R1, R2, ..., Rn)`

A 1 Gbit/s home network behind a 100 Mbit/s broadband line gives at most 100 Mbit/s to the internet. Throughput is also limited by the window/RTT bound above, and by competition with other flows sharing the bottleneck.

**Goodput** is throughput counting only useful application data. It excludes:

- headers at every layer (Ethernet, IP, TCP, TLS records)
- preamble and inter-frame gap on Ethernet
- retransmitted copies of lost packets
- protocol messages that carry no data (pure ACKs, handshakes)

In a one-direction untagged full-duplex 1 Gbit/s Ethernet model with 1500-byte IPv4 packets, minimal headers and nominal preamble/gap accounting, each full frame carries 1460 TCP payload bytes in 1538 byte-times: about 949 Mbit/s. Twelve bytes of TCP options reduce that to about 941 Mbit/s. These exclude application/TLS overhead and assume hosts, ACKs and congestion do not limit the rate. If 2% of equal-sized transmissions represent extra attempts, a saturated-link accounting model loses another 2% of useful rate; actual loss can also trigger congestion control.

## Which one matters?

Small transfers are often sensitive to round trips, while sufficiently large transfers can be limited by sustained goodput. Server work, congestion and host performance can dominate either.

> [!example] A 20 KB API response versus a 1 GB download
> Hypothetical path: 100 Mbit/s payload rate, 40 ms RTT. Ignore DNS, server work, loss, slow start and additional overhead; use TCP plus a full TLS 1.3 handshake with no resumption, early data or retry.
> - 20 KB: transmission is 160,000 / 10⁸ = 1.6 ms. In this model TCP setup and TLS setup consume two RTTs before the request, then one more RTT for the request and response: about 120 ms before adding the 1.6 ms response transmission. Round trips account for about 99% of that simplified total.
> - 1 GB: transmission is 8 × 10⁹ / 10⁸ = 80 s. The handshakes are noise.

Connection reuse and closer servers can cut round-trip costs. TLS/QUIC handshake choices also matter: 0-RTT requires prior connection state and appropriate replay-safe application handling; it is not available for every first connection. Which improvement helps most requires a workload and path measurement. A universal bandwidth threshold beyond which pages stop benefiting is omitted because no such general threshold is established here.

## Key takeaways
- Bandwidth is bits per second; latency is time. They measure different properties; raising link rate can reduce transmission and queueing delay, but not propagation time on an unchanged path.
- Per-hop delay = processing + queueing + transmission (L/R) + propagation (d/s). Store-and-forward pays transmission on every link.
- Signals in fibre travel about 200,000 km/s, roughly 5 µs per km. Distance puts a hard floor under RTT.
- Queueing delay grows sharply as utilisation approaches 100%: at 90% load the average wait is about 9 packet times in the simple model.
- Bandwidth-delay product is how much data must be in flight to fill a path; throughput ≤ window / RTT.
- Goodput is less than link rate because of headers, framing, retransmissions and control traffic.

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
