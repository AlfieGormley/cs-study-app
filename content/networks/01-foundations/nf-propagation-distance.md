---
id: nf-propagation-distance
sourceLesson: nf-performance
title: Distance and propagation delay
level: basic
minutes: 3
summary: Calculate a signal’s travel time and the propagation floor beneath round trips.
---

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

For a common teaching approximation to solid-glass fibre and some cables, v is roughly 2 × 10⁸ m/s, about two-thirds of the speed of light (the physical-media units explain why). That gives a handy rule:

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

## Key takeaways
- Propagation follows route length and signal speed.
- A faster link rate alone leaves propagation time unchanged.

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
