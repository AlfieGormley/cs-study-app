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

The labels are the four delays explained below: queueing (d_queue), transmission (d_trans), propagation (d_prop) and processing at the far end (d_proc).

### 1. Transmission delay

The time to push all the packet's bits onto the link. Use it whenever the question is "how long does this link take to send this much data?":

```formula
d_trans = L / R
where
d_trans: the transmission delay, in seconds: the time from the first bit of the packet going onto the link to the last bit going on
L: the packet length, in bits, counted at the layer being modelled
R: the link's transmission rate (bandwidth), in bits per second
In words: double the packet and the transmission time doubles; double the link rate and it halves. The length of the cable plays no part.
```

For example, a 1500-byte packet on a 100 Mbit/s link:

```formula
L = 1500 B × 8 bit/B = 12,000 bit
R = 100 Mbit/s = 10⁸ bit/s
d_trans = 12,000 bit / (10⁸ bit/s)
d_trans = 0.00012 s = 120 µs
where
L: the packet length in bits
B: bytes; one byte is 8 bits
bit: one binary digit, the unit link rates are counted in
R: the link rate, in bits per second
Mbit/s: megabits per second; 1 Mbit is 1,000,000 bits
d_trans: the transmission delay
s: seconds
µs: microseconds; 1 µs is one millionth of a second (10⁻⁶ s)
In words: a 100 Mbit/s link needs 120 millionths of a second to put a 1500-byte packet onto the wire.
```

The table repeats this for other rates. It ignores additional framing and encoding overhead, which a real link adds on top. A 1500-byte packet is 12,000 bits:

| Link rate | d_trans |
|---|---|
| 10 Mbit/s | 1.2 ms |
| 100 Mbit/s | 120 µs |
| 1 Gbit/s | 12 µs |
| 10 Gbit/s | 1.2 µs |

### 2. Propagation delay

The time for a bit to travel the length of the medium. Use it whenever the question is "how long does a signal take to get there?":

```formula
d_prop = d / v
where
d_prop: the propagation delay, in seconds: how long one bit takes to travel from one end of the link to the other
d: the length of the link (the distance travelled), in metres
v: the signal's speed in the medium, in metres per second; roughly 2 × 10⁸ m/s in glass fibre and close to 3 × 10⁸ m/s for radio in air
In words: twice the distance takes twice as long; a faster medium takes less time. Packet size and link rate play no part.
```

For a common teaching approximation to solid-glass fibre and some cables, v is roughly 2 × 10⁸ m/s, about two-thirds of the speed of light (lesson 3 explains why). That gives a handy rule:

```formula
d_prop = 1000 m / (2 × 10⁸ m/s)
d_prop = 5 × 10⁻⁶ s = 5 µs
where
d_prop: the propagation delay over one kilometre of fibre
m: metres; 1000 m is one kilometre
m/s: metres per second, the unit of speed
s: seconds
µs: microseconds, millionths of a second
In words: in fibre, a signal needs about 5 µs for every kilometre, or 1 ms (millisecond, a thousandth of a second) for every 200 km.
```

Transmission and propagation are often confused. Transmission depends on the packet size and the link rate, and has nothing to do with distance. In this model, propagation depends on path length and signal speed, not packet size or bit rate. An upgrade that changes the medium, wavelength or route can also change propagation; increasing the rate alone does not.

> [!example] A hypothetical 5,600 km fibre route
> Assume 200,000 km/s propagation in both directions. The calculation below gives 28 ms one way, so the propagation contribution to RTT (round-trip time: there and back) is 56 ms. Longer routes and equipment add delay. This is a specified model, not a measured or universal city-pair RTT; such measured figures are omitted without a route and measurement source.

```formula
d_prop = d / v
d_prop = 5,600 km / (200,000 km/s)
d_prop = 0.028 s = 28 ms
RTT_prop = 2 × d_prop = 56 ms
where
d_prop: the one-way propagation delay
d: the route length, 5,600 kilometres (km)
v: the signal speed in the fibre, 200,000 km/s
RTT_prop: the part of the round-trip time caused by propagation alone: out and back
km: kilometres; km/s is kilometres per second
s: seconds
ms: milliseconds; 1 ms is a thousandth of a second
In words: 5,600 km of fibre takes 28 ms each way, so propagation alone puts at least 56 ms into every round trip on this route.
```

### 3. Queueing delay

If packets arrive at a router faster than its output link can send them, they wait in a buffer. Queueing delay can be zero on an idle link and hundreds of milliseconds on a congested one. Variation in packet delay is commonly called **jitter**; queueing is one contributor, not the only possible source.

### 4. Processing delay

The time for a device to examine the header, look up where to send the packet and check for errors. The value depends on the hardware, software, configured processing and load; no universal per-router timing is established here.

### Putting it together

The delay for one hop is the sum of the four parts:

```formula
d_hop = d_proc + d_queue + d_trans + d_prop
where
d_hop: the total delay for one hop (one link plus the device at its far end), in seconds
d_proc: the processing delay: time to examine the header and decide where the packet goes
d_queue: the queueing delay: time spent waiting in a buffer behind other packets; zero on an idle link
d_trans: the transmission delay, packet length divided by link rate
d_prop: the propagation delay, distance divided by signal speed
In words: a packet's time across one hop is the time it waits, plus the time to put it on the wire, plus the time to travel, plus the time to be examined. Add the hops together for the whole path.
```

The calculations below assume **store-and-forward**: a packet must arrive completely before it can be sent on, so the transmission delay is paid again on every link. Cut-through forwarding can overlap reception with onward transmission and needs a different model.

> [!example] Two-hop calculation
> Ignore framing overhead and assume store-and-forward. Host A sends a 1500-byte packet to host B through one router. Both links run at 100 Mbit/s; they are 200 km and 800 km long. The router takes 20 µs to process the packet and there is no queue.

Store-and-forward means the packet is transmitted twice, once on each link. Propagation covers the 1,000 km of the two links together:

```formula
d_trans = 12,000 bit / (10⁸ bit/s)
d_trans = 120 µs
d_prop = 1,000 km × 5 µs/km = 5,000 µs
d_total = 2 × d_trans + d_prop + d_proc
d_total = (240 + 5,000 + 20) µs
d_total = 5,260 µs ≈ 5.26 ms
where
d_trans: the transmission delay on one 100 Mbit/s link for a 1500-byte (12,000-bit) packet
bit: one binary digit; bit/s is bits per second
s: seconds
d_prop: the propagation delay over both links together, at about 5 µs per kilometre
km: kilometres
µs: microseconds, millionths of a second
d_total: the end-to-end delay from A starting to send until B has the whole packet
d_proc: the router's processing delay, 20 µs
ms: milliseconds, thousandths of a second
≈: approximately equal to
In words: of the 5.26 ms total, 5 ms is the signal travelling 1,000 km; transmission and processing are small by comparison.
```

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

The question here is "how busy is this link, and how long will packets wait?" The **traffic intensity** compares the bits arriving each second with the bits the link can send each second:

```formula
ρ = L × a / R
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
W_q = ρ / (1 − ρ) × T_s
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

## The bandwidth-delay product

For a steady window-limited flow, how much unacknowledged data corresponds to a target payload rate? A sender learns that data arrived only when an acknowledgement (ACK) comes back, one round trip after sending it. To keep sending throughout that round trip, it needs a full round trip's worth of data in flight. Multiply the rate by the acknowledgement round-trip time, using consistent units:

```formula
BDP = R × RTT
where
BDP: the bandwidth-delay product, in bits: the amount of data sent but not yet acknowledged when the path is kept full
R: the target payload rate, in bits per second
RTT: the round-trip time: from sending data until its acknowledgement arrives, in seconds
In words: a fast or long path holds a lot of data "in the pipe" at once; double either the rate or the RTT and the data in flight doubles.
```

For a hypothetical payload rate of 1 Gbit/s and a 70 ms RTT:

```formula
BDP = 10⁹ bit/s × 0.070 s
BDP = 7 × 10⁷ bit = 70 Mbit
BDP = 70 Mbit / 8 = 8.75 MB
where
BDP: the bandwidth-delay product
bit: one binary digit; bit/s is bits per second
s: seconds; 70 ms is 0.070 s
Mbit: megabits; 1 Mbit is 1,000,000 bits
MB: megabytes; 1 MB is 1,000,000 bytes, and there are 8 bits in a byte
In words: to keep a 1 Gbit/s, 70 ms path full, about 8.75 MB must be sent and still awaiting acknowledgement at any moment.
```

That is how much a sender must have sent but not yet had acknowledged to keep the pipe full. If the sender's **window** (the amount it may have unacknowledged) is smaller than the BDP, it sits idle waiting for acknowledgements. It can send at most one window per round trip, so throughput is capped at:

```formula
X ≤ W / RTT
where
X: the throughput, in bits per second
W: the window: the most data the sender may have sent but not yet had acknowledged, in bits
RTT: the round-trip time, in seconds
≤: less than or equal to (this is an upper limit, not a prediction)
In words: one window per round trip is the most a window-limited sender can manage, however fast the link is.
```

> [!example] The original TCP window limit
> Without negotiated window scaling, TCP’s 16-bit advertised receive window cannot represent more than 65,535 bytes. This bounds steady new-data throughput when that window is the active constraint. Over a 70 ms RTT the calculation below caps throughput at about **7.5 Mbit/s**, no matter how fast the link is. The TCP **window scale** option (RFC 7323) allows larger receive windows when both endpoints negotiate it; support and configuration must be checked.

```formula
X ≤ (65,535 B × 8 bit/B) / 0.070 s
X ≤ 524,280 bit / 0.070 s
X ≤ 7.5 × 10⁶ bit/s = 7.5 Mbit/s
where
X: the throughput limit
B: bytes; one byte is 8 bits, so bit/B is bits per byte
bit: one binary digit
s: seconds; 70 ms is 0.070 s
Mbit/s: megabits per second (millions of bits per second)
In words: a 65,535-byte window delivered once every 70 ms is about 7.5 Mbit/s, under 1% of a gigabit link.
```

Paths with a large BDP are called **long fat networks**. They need large windows, large socket buffers and loss recovery that copes with many packets in flight. Lesson 6 and the TCP module build on this.

## Throughput and goodput

**Throughput** is the rate at which data actually gets through, as opposed to the link's nominal rate. End to end, it is limited by the slowest link on the path, the **bottleneck**:

```formula
X ≤ min(R_1, R_2, …, R_n)
where
X: the end-to-end throughput, in bits per second
R_1, R_2, R_n: the rates of the first, second and last links on the path, in bits per second
n: the number of links on the path
…: and so on, for every link in between
min: the minimum: the smallest of the values in the brackets
≤: less than or equal to
In words: a path can never carry data faster than its slowest link.
```

A 1 Gbit/s home network behind a 100 Mbit/s broadband line gives at most 100 Mbit/s to the internet, the smaller of the two rates. Throughput is also limited by the window/RTT bound above, and by competition with other flows sharing the bottleneck.

**Goodput** is throughput counting only useful application data. It excludes:

- headers at every layer (Ethernet, IP, TCP, TLS records)
- preamble and inter-frame gap on Ethernet
- retransmitted copies of lost packets
- protocol messages that carry no data (pure ACKs, handshakes)

In a one-direction untagged full-duplex 1 Gbit/s Ethernet model with 1500-byte IPv4 packets, minimal headers and nominal preamble/gap accounting, each full frame carries 1460 TCP payload bytes in 1538 byte-times (lesson 1):

```formula
G = (D / W) × R
G = (1460 / 1538) × 1000 Mbit/s
G ≈ 949 Mbit/s
where
G: the goodput, the rate of TCP payload delivered, in megabits per second (Mbit/s)
D: the TCP data per frame, 1460 bytes
W: the wire time per frame, 1538 byte-times (the 1500-byte IP packet plus 38 bytes of Ethernet header, FCS, preamble and gap)
R: the link rate, 1000 Mbit/s (1 Gbit/s)
Mbit/s: megabits per second; 1 Mbit is 1,000,000 bits
≈: approximately equal to
In words: about 95% of the gigabit link's time carries TCP payload, so about 949 Mbit/s of it is useful data.
```

Twelve bytes of TCP options reduce that to about 941 Mbit/s. These exclude application/TLS overhead and assume hosts, ACKs and congestion do not limit the rate. If 2% of equal-sized transmissions represent extra attempts, a saturated-link accounting model loses another 2% of useful rate; actual loss can also trigger congestion control.

## Which one matters?

Small transfers are often sensitive to round trips, while sufficiently large transfers can be limited by sustained goodput. Server work, congestion and host performance can dominate either.

> [!example] A 20 KB API response versus a 1 GB download
> Hypothetical path: 100 Mbit/s payload rate, 40 ms RTT. Ignore DNS, server work, loss, slow start and additional overhead; use TCP plus a full TLS 1.3 handshake with no resumption, early data or retry.
> - 20 KB: in this model TCP setup and TLS setup consume two RTTs before the request, then one more RTT for the request and response: about 120 ms before adding 1.6 ms of response transmission. Round trips account for about 99% of that simplified total.
> - 1 GB: transmission alone takes 80 s. The handshakes are noise.

```formula
t ≈ 3 × RTT + L / R
t ≈ 3 × 40 ms + 160,000 bit / (10⁸ bit/s)
t ≈ 120 ms + 1.6 ms ≈ 121.6 ms
L / R = 8 × 10⁹ bit / (10⁸ bit/s) = 80 s
where
t: the time until the whole 20 KB response has arrived
RTT: the round-trip time, 40 ms; three are spent on TCP setup, TLS setup and the request itself
L: the response size in bits: 20 KB (20,000 bytes) is 160,000 bits; 1 GB (10⁹ bytes) is 8 × 10⁹ bits
R: the payload rate, 100 Mbit/s = 10⁸ bits per second
ms: milliseconds, thousandths of a second
bit: one binary digit; bit/s is bits per second
s: seconds
≈: approximately equal to
In words: for the small response, 120 of the 121.6 ms are round trips, so only a shorter RTT or fewer round trips will help; for the 1 GB download, 80 s of transmission dwarfs the 120 ms of handshakes, so only more bandwidth will help.
```

Connection reuse and closer servers can cut round-trip costs. TLS/QUIC handshake choices also matter: 0-RTT requires prior connection state and appropriate replay-safe application handling; it is not available for every first connection. Which improvement helps most requires a workload and path measurement. A universal bandwidth threshold beyond which pages stop benefiting is omitted because no such general threshold is established here.

## Key takeaways
- Bandwidth is bits per second; latency is time. They measure different properties; raising link rate can reduce transmission and queueing delay, but not propagation time on an unchanged path.
- Per-hop delay is processing plus queueing plus transmission (packet bits divided by link rate) plus propagation (distance divided by signal speed). Store-and-forward pays transmission on every link.
- Signals in fibre travel about 200,000 km/s, roughly 5 µs per km. Distance puts a hard floor under RTT.
- Queueing delay grows sharply as utilisation approaches 100%: at 90% load the average wait is about 9 packet times in the simple model.
- Bandwidth-delay product (rate times RTT) is how much data must be in flight to fill a path; a window-limited sender gets at most one window per round trip.
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
