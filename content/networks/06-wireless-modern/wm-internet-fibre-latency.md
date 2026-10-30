---
id: wm-internet-fibre-latency
title: Fibre propagation and the distance budget
level: advanced
minutes: 3
summary: Propagation follows actual distance and signal speed, separately from queues and processing.
sourceLesson: wm-internet-structure
---

Bandwidth can be bought; the speed of light cannot. Over long distances, propagation time through fibre sets a floor on round-trip time that no upgrade removes, so distance is often the biggest single factor in latency.

## The physics of latency

Light in glass travels about a third slower than in a vacuum. For signal delay, what counts is the fibre's effective **group index** at the operating wavelength; this lesson assumes 1.47, close to Corning's characterised 1.4682 for SMF-28 Ultra at 1550 nanometres. That gives a speed of roughly 204,000 km/s, about **5 µs per km**.

```formula reference
RTT = (2d) / v
v = c / n
where
RTT: the propagation round-trip time: there and back, ignoring every other delay, in seconds (s)
d: the one-way fibre route length, in kilometres (km)
v: the speed of the signal in the fibre, about 204,000 kilometres per second (km/s)
c: the speed of light in a vacuum, about 299,792 km/s
n: the dimensionless effective group index used for signal delay, assumed to be 1.47 here; the actual value depends on fibre and wavelength
In words: light in fibre covers about 204 km every millisecond, so each 100 km of fibre route adds about 1 ms of round-trip time.
```

A useful rule: **about 1 ms of round-trip time per 100 km of fibre route**. The great-circle distance from London to New York is about 5,570 km, so even an ideal fibre laid along that line would give a propagation RTT of about 55 ms before any router or server adds anything; real cable routes are longer.

What this means in practice:

- **Bandwidth does not fix distance.** A faster link shortens the time to push the bits out, but not the time for them to travel. A ping across an ocean stays near its propagation floor after a 10× bandwidth upgrade.
- **Every round trip pays it again.** Protocols that need several exchanges before any useful data is sent (TCP and TLS handshakes, chains of dependent requests) multiply the distance penalty.
- **Real routes are longer than maps.** Cables follow coastlines and terrain, and return paths can differ, so measured RTTs exceed the map-distance estimate. Transmission, processing and queueing add more.

Shorter routes or nearer servers reduce propagation; reducing queueing can also reduce RTT without changing geography.

## Key takeaways
- Propagation follows actual distance and signal speed, separately from queues and processing.
- Hypothetical route calculations establish conditional bounds, not a measured city-pair RTT.

## Further reading
- [Corning: SMF-28 Ultra optical fibre, including effective group index](https://www.corning.com/content/dam/corning/media/worldwide/coc/documents/Fiber/product-information-sheets/PI-1424-AEN.pdf)
- [BIPM: SI Brochure, including the defined vacuum speed of light](https://www.bipm.org/documents/20126/41483022/SI-Brochure-9.pdf)
