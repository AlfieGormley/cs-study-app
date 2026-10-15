---
id: nf-complete-hop-delay
sourceLesson: nf-performance
title: Combine the four delays
level: basic
minutes: 4
summary: Add processing, queueing, transmission and propagation across store-and-forward hops.
---

## The four components of delay

When a packet crosses one hop (a link plus the device at the far end), its delay has four parts.

```
 queue    transmit     propagate
[ | | ]-> [=====]  ~~~~~~~~~~~~~~> router
 d_queue   d_trans      d_prop      d_proc
```

The labels are the four delays explained below: queueing (d_queue), transmission (d_trans), propagation (d_prop) and processing at the far end (d_proc).

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

When a message is split into several equal-size packets, different links can work on different packets at once. This is packet pipelining: the first packet still pays transmission at every store-and-forward hop, but later packets can follow at one packet time apart on equal-rate, initially idle links. This overlaps work across links without allowing two packets to transmit simultaneously on one link. Extra headers are excluded from this simple comparison.

The same arithmetic in Python:

```python
def hop_delay(bits, rate, km, proc=0.0,
              queue=0.0, speed=2e8):
    if (rate <= 0 or speed <= 0
            or min(bits, km, proc,
                   queue) < 0):
        raise ValueError("invalid delay")
    # Serialise all bits at the link rate.
    trans = bits / rate
    # Convert distance to metres first.
    prop = km * 1000 / speed
    return proc + queue + trans + prop


# Add two links; processing occurs once.
bits = 1500 * 8
total = (hop_delay(bits, 100e6, 200)
         + hop_delay(bits, 100e6, 800,
                     proc=20e-6))
print(f"{total * 1e3:.2f} ms")  # 5.26 ms
```

## Key takeaways
- A store-and-forward device receives a whole packet before sending it onward.
- Sum each relevant link’s transmission and propagation plus processing and queueing.

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
