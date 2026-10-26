---
id: nf-propagation-distance
sourceLesson: nf-performance
title: Distance and propagation delay
level: basic
minutes: 3
summary: Explain the propagation floor and distinguish route length from link rate.
---

Propagation delay is how long a signal takes to travel through the medium. A longer route takes longer; a medium with a higher signal speed takes less time.

## Distance sets a floor

In this model, propagation depends on route length and signal speed, rather than packet size or bit rate. Increasing the rate alone puts bits onto the link faster but does not make each bit travel faster.

```formula reference
d_prop = d / v
where
d_prop: one-way propagation delay in seconds
d: length of the signal's route in metres
v: signal speed in the medium in metres per second; roughly 200 million in ordinary solid-glass fibre and close to 300 million for radio in air
In words: propagation time grows with distance and falls with signal speed; halving the route length halves this delay.
```

A useful teaching approximation for ordinary solid-glass fibre is about 5 microseconds per kilometre, or 1 millisecond per 200 km. The precise value depends on fibre construction and wavelength; some cables also have different speeds.

For a hypothetical 5,600 km fibre route at 200,000 km/s, propagation takes 28 ms each way. If the return follows the same route and speed, propagation alone contributes 56 ms to the round-trip time (**RTT**, there and back). Processing, transmission and queueing add more.

These are specified-model results, not measured city-pair latencies. A real route may be longer than the distance on a map.

## What can improve it?

A shorter route or a faster propagation medium can reduce propagation delay. Radio in air travels faster than light in typical solid-glass fibre, but a real radio link has its own capacity, reliability and equipment constraints.

A higher bit rate or smaller packet can reduce transmission delay while leaving propagation unchanged. An upgrade that also changes the route, wavelength or medium may change both; identify which property actually changed.

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
